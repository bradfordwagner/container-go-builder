## 1. Ansible Role Setup

- [ ] 1.1 Add `andrewrothstein.goreleaser` at role version `v2.2.47` to `requirements.yml`
- [ ] 1.2 Set `goreleaser_version: v1.21.2` in `playbook.yml` vars
- [ ] 1.3 Add `andrewrothstein.goreleaser` role to `playbook.yml` roles list (after `bradfordwagner.golang`)

## 2. Documentation

- [ ] 2.1 Add installed tools table to `README.md` listing goreleaser v1.21.2
- [ ] 2.2 Update `AGENTS.md` project overview to mention goreleaser
- [ ] 2.3 Update `AGENTS.md` key files table for `requirements.yml` and `playbook.yml` entries
- [ ] 2.4 Update `AGENTS.md` bumping dependencies section with goreleaser version instructions

## 3. Verification

- [ ] 3.1 Push feature branch and confirm all 8 matrix build jobs pass (ubuntu_noble + debian_bookworm-slim × amd64 + arm64 × Go 1.25 + 1.26)
- [ ] 3.2 Pull a built image locally and run `docker run --rm <image> goreleaser --version` to confirm the binary is present and reports v1.21.2
