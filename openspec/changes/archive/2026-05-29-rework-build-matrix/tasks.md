## 1. config.yaml

- [x] 1.1 Add `push_enabled: false` field
- [x] 1.2 Add top-level `go_versions` list (e.g., `["1.22", "1.23"]`)
- [x] 1.3 Add top-level `upstream` block with `image` and `tag`
- [x] 1.4 Add top-level `runtime` block with `image` and `tag`
- [x] 1.5 Simplify `builds` entries to `os` + `archs` list (remove old upstream/tag_suffix fields)

## 2. Dockerfile

- [x] 2.1 Add `ARG UPSTREAM` and change `FROM` to `FROM ${UPSTREAM} AS base`
- [x] 2.2 Add `ARG GO_VERSION` and pass `-e go_version=${GO_VERSION}` to `ansible-playbook`

## 3. Matrix generation script

- [x] 3.1 Write a script (e.g., `scripts/matrix.py`) that reads `config.yaml` and emits a JSON array of `{ os, arch, go_version, runner, upstream_ref, runtime_ref, push_enabled }` entries
- [x] 3.2 Include arch→runner mapping (`linux/amd64`→`ubuntu-24.04`, `linux/arm64`→`ubuntu-24.04-arm`)
- [x] 3.3 Derive `upstream_ref` as `<upstream.image>:<upstream.tag>`
- [x] 3.4 Derive `runtime_ref` as `<runtime.image>:<runtime.tag>`

## 4. Branch build workflow

- [x] 4.1 Rewrite `.github/workflows/container_branches.yml` — remove all Dagger steps
- [x] 4.2 Add `matrix` job: installs `yq` or uses `python3`, runs `scripts/matrix.py`, outputs JSON matrix and `push_enabled`
- [x] 4.3 Add `build` job: uses `runs-on: ${{ matrix.product.runner }}`, login to ghcr.io, `docker build` with `--build-arg UPSTREAM` and `--build-arg GO_VERSION`, conditional `docker push` of arch-qualified tag when `push_enabled=true`
- [x] 4.4 Add `manifest` job: `needs: [build]`, loops over `go_version+os` combinations, runs `docker manifest create` + `docker manifest push` when `push_enabled=true`
- [x] 4.5 Ensure branch builds never push regardless of `push_enabled` (hardcode push skip for branch workflow or gate on `github.ref == 'refs/heads/main'`)

## 5. Daily cron workflow

- [x] 5.1 Create `.github/workflows/daily_build.yml` with `on: schedule: - cron: '0 13 * * *'` (8am EST) and `workflow_dispatch`
- [x] 5.2 Reuse the same `matrix` → `build` → `manifest` job structure as the branch workflow
- [x] 5.3 Publish is controlled solely by `push_enabled` in `config.yaml` (no extra override logic)

## 6. Cleanup

- [x] 6.1 Delete `.github/workflows/container_tags.yml`
- [x] 6.2 Remove `bin/dagger` or any Dagger-related files if present
