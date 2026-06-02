# container-go-builder
Image build for https://quay.io/repository/bradfordwagner/go-builder?tab=tags

Ansible-provisioned builder image with Go and goreleaser installed, built across a matrix of OS × arch × go_version.

## Installed Tools

| Tool | Version |
|------|---------|
| Go | see `go_versions` in `config.yaml` |
| goreleaser | v1.21.2 |
