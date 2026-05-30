## Context

The repo builds a Go builder container image (an Ansible-provisioned image with Go installed) and publishes it to `ghcr.io/bradfordwagner/go-builder`. The current system delegates all build logic to an external Dagger module, which is opaque and only supports a single `os+arch` axis. We need a transparent, bespoke build system that adds a `go_version` axis and produces multi-arch manifests tagged by `go_version+os`.

Current files of interest:
- `config.yaml` — declarative build config (target repo, upstream image, os/arch list)
- `Dockerfile` — single-stage, takes `OS` ARG
- `.github/workflows/container_branches.yml` — branch builds via Dagger
- `.github/workflows/container_tags.yml` — tag builds via Dagger (to be removed)

## Goals / Non-Goals

**Goals:**
- Three-axis matrix: `os × arch × go_version`, fully declared in `config.yaml`
- Multi-stage Dockerfile parameterized by `OS`, `ARCH`, `GO_VERSION`; upstream base image resolved per `os+arch` from config
- Native `docker buildx build` + `docker manifest` pipeline — no external build framework
- Single manifest per `go_version+os` combining all arch variants; tag: `go-builder:<go_version>-<os>`
- `push_enabled` boolean in `config.yaml` gates all pushes; `false` by default, set `true` to publish
- Daily cron on `main` runs the full matrix and publishes (assumes `push_enabled: true` in committed config)
- Branch builds always run (for CI validation) but never push

**Non-Goals:**
- Git-tag-based versioning or releases
- Multi-registry publishing (ghcr.io only)
- Caching layers between runs (keep it simple)

## Decisions

### 1. Native arch runners — one runner per arch

**Decision:** Each build matrix entry runs on a GitHub-hosted runner that natively matches the target arch. `linux/amd64` → `ubuntu-24.04`; `linux/arm64` → `ubuntu-24.04-arm`. Plain `docker build` (no `--platform` flag, no QEMU).

**Rationale:** QEMU emulation is slow and can produce subtly different binaries. Native runners give full-speed builds and accurate results. GitHub-hosted ARM runners are now generally available.

The runner label is derived from the arch in the matrix job via a static map embedded in the generation script (amd64→`ubuntu-24.04`, arm64→`ubuntu-24.04-arm`). Adding a new arch requires updating that map.

**Alternative considered:** Single amd64 runner with `docker buildx --platform` — rejected due to QEMU overhead and emulation risk.

---

### 2. `config.yaml` as single source of truth

**Decision:** All matrix values (`go_versions`, `builds`, `upstream`, `runtime`, `push_enabled`) live in `config.yaml`. Workflows read this file via a dedicated `matrix` job that emits a JSON array consumed by `strategy.matrix`.

**Schema:**
```yaml
target_repo: ghcr.io/bradfordwagner/go-builder
push_enabled: false

go_versions:
  - "1.22"
  - "1.23"

upstream:
  image: ghcr.io/bradfordwagner/ansible
  tag: 6.3.1

runtime:
  image: ghcr.io/bradfordwagner/base
  tag: 6.3.1

builds:
  - os: alpine          # used in image tag: go-builder:<go_version>-<os>
    archs:
      - linux/amd64
      - linux/arm64
```

`upstream` is the Ansible base image pulled natively by the runner (multi-arch manifest — Docker resolves the correct arch automatically). `runtime` is the container image used for the CI job itself (i.e., `jobs.<job>.container`), pinning the build environment.

Each expanded matrix entry: `{ os, arch, go_version, runner, upstream_ref, runtime_ref }` where `runner` and `upstream_ref` are derived by the matrix job.

**Rationale:** Keeps workflow YAML free of hardcoded values; changing the matrix requires only a `config.yaml` edit.

---

### 3. Matrix job emits JSON for GitHub Actions strategy

**Decision:** A `matrix` job runs first, reads `config.yaml` with a small shell script (using `yq`), and outputs a JSON array. The `build` job consumes it via `fromJSON(needs.matrix.outputs.matrix)`.

Each matrix entry contains: `{ os, arch, go_version, upstream_image, tag_suffix }`.

**Rationale:** GitHub Actions native matrix is the simplest fan-out mechanism. A JSON-producing job is a well-established pattern that avoids a separate matrix-generation tool.

---

### 4. Multi-stage Dockerfile

**Decision:**
```dockerfile
ARG UPSTREAM
FROM ${UPSTREAM} AS base

ARG GO_VERSION
COPY . /src
WORKDIR /src
RUN ansible-galaxy install -r requirements.yml \
 && ansible-playbook playbook.yml -e go_version=${GO_VERSION} \
 && rm -rf /src
```

`UPSTREAM` is `<upstream.image>:<upstream.tag>` — Docker on the native-arch runner pulls the correct arch variant from the multi-arch manifest automatically, so no per-arch tag suffix is needed. `GO_VERSION` is passed as a build-arg. The existing Ansible role (`bradfordwagner.golang`) is retained.

**Rationale:** Minimal change to existing logic; native runner + multi-arch upstream manifest eliminates the need for explicit arch resolution in the Dockerfile or matrix job.

---

### 5. Manifest assembly with `docker manifest`

**Decision:** After all `build` jobs complete, a `manifest` job loops over each `go_version+os` combination, creates a manifest from the per-arch images (pushed with an `<tag>-<arch>` suffix during the build phase), and pushes the final multi-arch manifest.

Per-arch intermediate tag: `go-builder:<go_version>-<tag_suffix>-<arch>`
Final manifest tag: `go-builder:<go_version>-<tag_suffix>`

**Rationale:** `docker manifest` is available on all GitHub-hosted runners and requires no extra tooling.

---

### 6. `push_enabled` in `config.yaml`

**Decision:** The matrix job reads `push_enabled` from `config.yaml` and passes it as a job output. Build and manifest jobs conditionally skip push steps when it is `false`.

**Rationale:** Single toggle, declarative, version-controlled. No workflow dispatch inputs or env var juggling needed.

---

### 7. Remove `container_tags.yml`

**Decision:** Delete the tag-based publish workflow entirely.

**Rationale:** Image versioning is expressed through `go_version` in the tag. Git tags add no value here.

## Risks / Trade-offs

- **`yq` availability on runners** → Mitigation: pin a specific `yq` install step; `mikefarah/yq` has a stable GitHub Action. Alternatively generate the matrix JSON with `python3 -c` + PyYAML (pre-installed on all GitHub runners) to avoid extra install.
- **ARM runner availability** → Mitigation: `ubuntu-24.04-arm` is GA on GitHub-hosted runners; if unavailable for a repo, self-hosted ARM runner can substitute with the same label.
- **`docker manifest` requires experimental features on older Docker versions** → Mitigation: GitHub-hosted `ubuntu-24.04` runners ship Docker 27+, which supports `docker manifest` without experimental flags.
- **Matrix explosion** (many `os × arch × go_version` combos consume runner minutes) → Mitigation: keep the initial `config.yaml` small; `fail-fast: false` so one failure doesn't abort others.
- **`push_enabled: true` accidentally committed** → Mitigation: document clearly in `config.yaml` comments; the daily cron workflow will override nothing — it simply uses whatever is in the file.
