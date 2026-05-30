## Why

The current build system delegates all build logic to an external Dagger module (`bradfordwagner/dagger-container-builds`), which is opaque, hard to debug, and does not support a Go version dimension in the image matrix. A bespoke, declarative build system will give full visibility and control over the `os × arch × go_version` matrix needed to produce versioned Go builder images.

## What Changes

- **BREAKING**: Remove Dagger-based workflow steps; replace with native `docker buildx` + `docker manifest` commands
- **BREAKING**: Remove tag-based publish workflow (`container_tags.yml`); versioning is handled via Go version in the image tag, not git tags
- Replace single-dimension `os+arch` config with a three-dimension matrix: `os`, `arch`, `go_version`
- Rework `config.yaml` to declare the full matrix and per-`os+arch` upstream base image mapping
- Rework `Dockerfile` to a multi-stage build: upstream base (resolved per `os+arch`) → Go install layer
- GitHub Actions matrix strategy fans out builds across all `os × arch × go_version` combinations
- Add a manifest-assembly job that stitches per-arch images into a multi-arch manifest per `go_version+os`
- Tag format: `go-builder:<go_version>-<os>`
- Images are only published on the `main` branch via a daily cron; branch builds run but do not push
- A single `push_enabled` boolean in `config.yaml` gates all registry pushes — flip it locally and commit to test publish behavior from any branch without touching workflow logic

## Capabilities

### New Capabilities

- `build-matrix`: Declarative `os × arch × go_version` matrix in `config.yaml`; Dockerfile accepts `OS`, `ARCH`, `GO_VERSION` build-args and uses a multi-stage build with an upstream base image resolved per `os+arch`
- `manifest-assembly`: Post-build job that uses `docker manifest` (or `manifest-tool`) to combine per-arch images into a single multi-arch manifest tagged `go-builder:<go_version>-<os>`
- `daily-cron`: GitHub Actions scheduled workflow that runs the full matrix build daily to keep Go builder images up to date; publish behavior controlled by `push_enabled` in `config.yaml`

### Modified Capabilities

## Impact

- `.github/workflows/container_branches.yml` — rewritten; Dagger removed
- `.github/workflows/container_tags.yml` — rewritten; Dagger removed
- `config.yaml` — schema extended with `go_versions` list and per-`os+arch` upstream image mapping
- `Dockerfile` — converted to multi-stage build parameterized by `OS`, `ARCH`, `GO_VERSION`
- New workflow file: `.github/workflows/daily_build.yml`
- Removes dependency on `https://github.com/bradfordwagner/dagger-container-builds`
