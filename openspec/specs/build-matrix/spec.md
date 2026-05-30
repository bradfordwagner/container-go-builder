## ADDED Requirements

### Requirement: config.yaml declares the full build matrix
`config.yaml` SHALL be the sole source of truth for all build parameters. It MUST contain: `target_repo`, `push_enabled`, `go_versions` (list), `upstream` (image + tag), `runtime` (image + tag), and `builds` (list of os + archs). Builds entries SHALL NOT contain per-build upstream overrides — all refs are derived from top-level blocks.

#### Scenario: Valid config is parsed into a matrix
- **WHEN** the matrix job reads `config.yaml`
- **THEN** it emits a JSON array where each entry contains `{ os, arch, arch_short, go_version, runner, upstream_ref, runtime_ref, target_repo, push_enabled }`

#### Scenario: Multiple go_versions expand the matrix
- **WHEN** `go_versions` contains N versions and `builds` contains M os+arch combinations
- **THEN** the emitted matrix contains N × M entries (one per go_version × os × arch triple)

#### Scenario: push_enabled is propagated
- **WHEN** the matrix job reads `push_enabled` from `config.yaml`
- **THEN** it emits `push_enabled` as a job output and embeds it in each matrix entry

---

### Requirement: upstream_ref and runtime_ref include the OS suffix
`scripts/matrix.py` SHALL derive `upstream_ref` as `<upstream.image>:<upstream.tag>-<os>` and `runtime_ref` as `<runtime.image>:<runtime.tag>-<os>`. This selects the OS-specific variant of each image; Docker resolves the correct arch automatically from the multi-arch manifest on the native runner.

#### Scenario: upstream_ref includes OS suffix
- **WHEN** `upstream.image=ghcr.io/bradfordwagner/ansible`, `upstream.tag=6.3.1`, and `os=noble`
- **THEN** `upstream_ref=ghcr.io/bradfordwagner/ansible:6.3.1-noble`

#### Scenario: runtime_ref includes OS suffix
- **WHEN** `runtime.image=ghcr.io/bradfordwagner/base`, `runtime.tag=4.3.2`, and `os=bookworm-slim`
- **THEN** `runtime_ref=ghcr.io/bradfordwagner/base:4.3.2-bookworm-slim`

---

### Requirement: matrix.py supports builds and manifests output modes
`scripts/matrix.py` SHALL accept an optional positional argument. With no argument or `builds`, it outputs the full build matrix array. With `manifests`, it outputs a deduplicated array of `{ go_version, os, target_repo, push_enabled, arch_shorts[] }` entries for use by the manifest job.

#### Scenario: Default mode outputs build matrix
- **WHEN** `python3 scripts/matrix.py` is run with no arguments
- **THEN** it outputs a JSON array with one entry per os × arch × go_version combination

#### Scenario: Manifests mode outputs deduplicated manifest entries
- **WHEN** `python3 scripts/matrix.py manifests` is run
- **THEN** it outputs a JSON array with one entry per go_version × os combination, each containing an `arch_shorts` list

---

### Requirement: Each build runs on a native-arch runner
The build job SHALL select a GitHub Actions runner that natively matches the target arch. `linux/amd64` MUST map to `ubuntu-24.04`; `linux/arm64` MUST map to `ubuntu-24.04-arm`.

#### Scenario: amd64 build uses x86 runner
- **WHEN** a matrix entry has `arch: linux/amd64`
- **THEN** the job runs on `ubuntu-24.04`

#### Scenario: arm64 build uses ARM runner
- **WHEN** a matrix entry has `arch: linux/arm64`
- **THEN** the job runs on `ubuntu-24.04-arm`

---

### Requirement: Dockerfile accepts UPSTREAM and GO_VERSION build-args
The Dockerfile SHALL be a multi-stage build parameterized by `UPSTREAM` (OS-specific upstream image reference) and `GO_VERSION`. It MUST use `FROM ${UPSTREAM} AS base` as the first stage and install Go via the existing Ansible role passing `go_version=${GO_VERSION}`.

#### Scenario: Build-args are passed during docker build
- **WHEN** a build job runs `docker build`
- **THEN** it passes `--build-arg UPSTREAM=<upstream_ref>` and `--build-arg GO_VERSION=<go_version>`

#### Scenario: Native runner resolves correct arch from upstream manifest
- **WHEN** `docker build` pulls `${UPSTREAM}` on a native-arch runner
- **THEN** Docker resolves the arch-correct layer from the upstream multi-arch manifest without any `--platform` flag

---

### Requirement: Per-arch images are pushed with an arch-qualified tag
When `push_enabled` is `true`, each build job SHALL push the built image with tag `<go_version>-<os>-<arch_short>`. These are intermediate tags consumed by the manifest job.

#### Scenario: Intermediate tag is pushed on push_enabled=true
- **WHEN** `push_enabled` is `true` and a build for `go_version=1.25`, `os=noble`, `arch=linux/arm64` completes
- **THEN** the image is pushed as `go-builder:1.25-noble-arm64`

#### Scenario: No push on push_enabled=false
- **WHEN** `push_enabled` is `false`
- **THEN** the build step runs but no `docker push` is executed
