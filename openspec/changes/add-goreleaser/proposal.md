## Why

The go-builder image is used as a CI/CD build environment. Adding goreleaser brings release automation tooling into the image so downstream pipelines can produce tagged releases without installing goreleaser separately at runtime.

## What Changes

- Add `andrewrothstein.goreleaser` Ansible Galaxy role to `requirements.yml` (pinned to `v2.2.47`)
- Set `goreleaser_version: v1.21.2` in `playbook.yml` and apply the role after `bradfordwagner.golang`
- Update `README.md` with an installed tools table listing goreleaser version
- Update `AGENTS.md` to reflect goreleaser in the project overview, key files table, and bumping dependencies section

## Capabilities

### New Capabilities

- `goreleaser-install`: Install goreleaser into the builder image via the `andrewrothstein.goreleaser` Ansible role, pinned to a specific version

### Modified Capabilities

<!-- No existing spec-level requirements are changing -->

## Impact

- `requirements.yml`: new role dependency
- `playbook.yml`: new role invocation + version var
- All build matrix variants (ubuntu_noble, debian_bookworm-slim × linux/amd64, linux/arm64 × Go 1.25, 1.26) now include goreleaser in the output image
- Image size increases by the goreleaser binary (~50MB compressed)
