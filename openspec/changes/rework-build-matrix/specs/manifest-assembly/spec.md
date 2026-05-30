## ADDED Requirements

### Requirement: Manifest job runs its own matrix from scripts/matrix.py manifests
The manifest job SHALL use a separate matrix produced by `python3 scripts/matrix.py manifests`, which emits one entry per unique `go_version+os` combination. Each entry contains `arch_shorts` — the list of arch suffixes built for that combination. This is computed in the same `matrix` job that produces the build matrix.

#### Scenario: Manifest matrix is generated alongside build matrix
- **WHEN** the `matrix` job runs
- **THEN** it emits both a `builds` output (full build matrix) and a `manifests` output (deduplicated go_version+os entries with arch_shorts)

#### Scenario: Manifest job fans out per go_version+os
- **WHEN** `go_versions: ["1.25", "1.26"]` and `builds: [{os: noble}, {os: bookworm-slim}]`
- **THEN** the manifest matrix contains 4 entries: `1.25-noble`, `1.26-noble`, `1.25-bookworm-slim`, `1.26-bookworm-slim`

---

### Requirement: Manifest job assembles a multi-arch manifest per go_version+os
After all build jobs complete, the `manifest` job SHALL use `docker manifest create` to combine the per-arch intermediate images into a single multi-arch manifest and push it tagged as `<go_version>-<os>`.

#### Scenario: Manifest created from per-arch images
- **WHEN** builds for `go_version=1.25`, `os=noble` have produced `go-builder:1.25-noble-amd64` and `go-builder:1.25-noble-arm64`
- **THEN** the manifest job creates and pushes `go-builder:1.25-noble` referencing both arch images

#### Scenario: Manifest job is skipped when push_enabled=false
- **WHEN** `push_enabled` is `false`
- **THEN** the manifest job skips all `docker manifest` and `docker push` steps

---

### Requirement: Manifest job depends on all build jobs
The manifest job SHALL declare `needs: [matrix, build]` so it only runs after every matrix build job has succeeded and the manifest matrix output is available.

#### Scenario: Manifest waits for all builds
- **WHEN** any build job in the matrix is still running
- **THEN** the manifest job does not start

#### Scenario: Manifest is skipped on build failure
- **WHEN** any build job fails and `fail-fast: false` is set
- **THEN** the manifest job does not run

---

### Requirement: Final manifest tag format is go_version-os
The pushed manifest tag SHALL follow the format `<go_version>-<os>` exactly as declared in `config.yaml`. No additional suffixes or prefixes are added.

#### Scenario: Tag matches config values
- **WHEN** `go_versions: ["1.25", "1.26"]` and `builds: [{os: noble}, {os: bookworm-slim}]`
- **THEN** the manifest job pushes `go-builder:1.25-noble`, `go-builder:1.26-noble`, `go-builder:1.25-bookworm-slim`, `go-builder:1.26-bookworm-slim`
