# AGENTS.md

## Project Overview

Builds and publishes a Go builder container image (`ghcr.io/bradfordwagner/go-builder`) using a bespoke native Docker pipeline. The image is an Ansible-provisioned base with Go installed, produced across a three-axis matrix: `os × arch × go_version`.

## Key Files

| File | Purpose |
|------|---------|
| `config.yaml` | Single source of truth for the full build matrix |
| `Dockerfile` | Multi-stage build: ansible upstream → lean runtime base |
| `scripts/matrix.py` | Reads `config.yaml`, emits JSON for GitHub Actions matrix strategy |
| `requirements.yml` | Ansible Galaxy role pin (`bradfordwagner.golang`) |
| `playbook.yml` | Ansible playbook that installs Go |
| `.github/workflows/container_branches.yml` | Branch build workflow; push gated by `push_enabled` |
| `.github/workflows/daily_build.yml` | Daily cron (8am EST); always pushes regardless of `push_enabled` |

## config.yaml Schema

```yaml
target_repo: ghcr.io/bradfordwagner/go-builder
push_enabled: false          # flip to true to publish from a branch build

go_versions:
  - "1.25"

upstream:
  image: ghcr.io/bradfordwagner/ansible
  tag: 6.3.1                 # OS suffix is appended automatically: tag-os

runtime:
  image: ghcr.io/bradfordwagner/base
  tag: 4.3.2                 # OS suffix is appended automatically: tag-os

builds:
  - os: ubuntu_noble
    archs:
      - linux/amd64
      - linux/arm64
```

- `upstream_ref` is derived as `upstream.image:upstream.tag-os`
- `runtime_ref` is derived as `runtime.image:runtime.tag-os`
- OS names must match actual image tags (e.g. `ubuntu_noble`, `debian_bookworm-slim`)

## Matrix Script

```bash
python3 scripts/matrix.py            # build matrix (one entry per os×arch×go_version)
python3 scripts/matrix.py manifests  # manifest matrix (one entry per go_version×os)
```

PyYAML is pre-installed on GitHub runners. Locally, run inside a venv with `pyyaml` installed.

## Image Tags

- Per-arch intermediate: `go-builder:<go_version>-<os>-<arch_short>` (e.g. `1.25-ubuntu_noble-arm64`)
- Final manifest: `go-builder:<go_version>-<os>` (e.g. `1.25-ubuntu_noble`)

## Build System

### Runners

| Arch | Runner |
|------|--------|
| `linux/amd64` | `ubuntu-24.04` |
| `linux/arm64` | `ubuntu-24.04-arm` |

Native arch runners — no QEMU, no `--platform` flag. Docker resolves the correct arch from upstream multi-arch manifests automatically.

### Dockerfile

Multi-stage: first stage uses the OS-specific ansible image to run the Ansible playbook and install Go; second stage copies `/usr/local` from build into the lean runtime base.

`--provenance=false` is required on `docker build` to produce Docker v2 manifest format. Without it, Docker Desktop's containerd image store outputs OCI index format, which breaks `dive` and some tooling.

### push_enabled

- **Branch builds**: gated on `push_enabled: true` in `config.yaml`. Set to `true` and push to test publishing from a feature branch.
- **Daily cron**: always pushes, ignores `push_enabled`.
- **No tag-based builds**: `container_tags.yml` has been removed.

## Bumping Dependencies

- **Go version**: add/remove entries in `go_versions` in `config.yaml`
- **Upstream ansible image**: update `upstream.tag`
- **Runtime base image**: update `runtime.tag`
- **Ansible golang role**: update `version` in `requirements.yml`

## Testing a Build Locally

```bash
# Activate a venv with pyyaml first, or use the system python if pyyaml is available
python3 scripts/matrix.py | jq .
python3 scripts/matrix.py manifests | jq .

# Build one variant locally (example)
docker build --provenance=false \
  --build-arg UPSTREAM=ghcr.io/bradfordwagner/ansible:6.3.1-ubuntu_noble \
  --build-arg RUNTIME=ghcr.io/bradfordwagner/base:4.3.2-ubuntu_noble \
  --build-arg GO_VERSION=1.25 \
  -t go-builder:1.25-ubuntu_noble-amd64 .

# Inspect layers
dive go-builder:1.25-ubuntu_noble-amd64
```

`dive` requires Docker Desktop's containerd image store to be **disabled** (Settings → General → uncheck "Use containerd for pulling and storing images").

## Triggering the Daily Build Manually

```bash
gh workflow run daily_build.yml --repo bradfordwagner/container-go-builder --ref main
```

## OpenSpec Specs

Canonical specs live under `openspec/specs/`:
- `build-matrix/spec.md` — config schema, matrix script behavior, runner selection, Dockerfile args
- `daily-cron/spec.md` — cron schedule, push gating rules, tag workflow removal
- `manifest-assembly/spec.md` — manifest job matrix, docker manifest assembly, tag format
