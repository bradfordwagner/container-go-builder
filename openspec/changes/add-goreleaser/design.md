## Context

The go-builder image currently installs Go via the `bradfordwagner.golang` Ansible role. Downstream pipelines that need goreleaser must install it themselves, adding per-job overhead and introducing version drift across repos. Bundling goreleaser into the builder image centralizes version control and eliminates per-job install steps.

## Goals / Non-Goals

**Goals:**
- Install goreleaser at a pinned version into all build matrix variants
- Verify the binary with a checksum from the role's built-in map
- No additional roles required in `requirements.yml` beyond `andrewrothstein.goreleaser`

**Non-Goals:**
- Goreleaser configuration or `.goreleaser.yaml` templating
- Upgrading goreleaser automatically (version is explicitly pinned)
- Installing goreleaser Pro

## Decisions

**Use `andrewrothstein.goreleaser` over a shell task**
The role handles cross-platform arch mapping, checksum verification, and download URL construction. A raw `get_url` + `unarchive` task would replicate this logic. The role pulls in `andrewrothstein.unarchivedeps` as a transitive dependency (ensures `tar`/`unzip` are present) and is actively maintained (v2.2.47, April 2025).

**Pin goreleaser to v1.21.2**
v1.21.2 is present in the role's built-in checksum map for `Linux_x86_64` and `Linux_arm64`, matching both target arches. This version is compatible with the downstream pipelines that will consume this image.

**Apply goreleaser role after `bradfordwagner.golang`**
Ordering is cosmetic (goreleaser is a standalone binary), but placing it after Go signals intent: this is a Go toolchain image.

## Risks / Trade-offs

- [Version staleness] → goreleaser v1.21.2 is ~2 major versions behind v2.x. Downstream consumers must not rely on v2-only features. Mitigation: version is explicitly documented in `README.md` and `playbook.yml`.
- [Image size] → goreleaser binary adds ~50MB to the image. Mitigation: acceptable for a builder image; no runtime containers consume this image.
- [Checksum coverage] → if a future goreleaser version is not in the role's checksum map, the install will fail or skip verification. Mitigation: always pick a version present in `defaults/main.yml` of the pinned role version.
