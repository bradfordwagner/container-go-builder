## ADDED Requirements

### Requirement: Daily cron workflow always builds and pushes
A GitHub Actions workflow SHALL run daily at 8am EST (13:00 UTC, cron `0 13 * * *`) on the default branch (`main`) and execute the full `os × arch × go_version` build matrix. It SHALL always push images and assemble manifests — `push_enabled` in `config.yaml` is ignored by this workflow.

#### Scenario: Workflow triggers on schedule
- **WHEN** the cron schedule fires (daily)
- **THEN** the full matrix build, push, and manifest assembly runs automatically on the default branch

#### Scenario: workflow_dispatch allows triggering on any branch
- **WHEN** a user manually triggers the workflow via `workflow_dispatch` and selects a feature branch
- **THEN** the daily build runs against that branch's code, enabling testing without a cron on main

#### Scenario: Cron always pushes regardless of push_enabled
- **WHEN** the cron workflow runs and `push_enabled: false` in `config.yaml`
- **THEN** images are still pushed and manifests assembled

---

### Requirement: Branch builds publish only when push_enabled is true
The branch workflow SHALL trigger on all branch pushes and run the full build matrix. Push and manifest assembly SHALL be gated on `push_enabled` in `config.yaml`, identical to the daily build workflow. This allows testing publish behavior from any branch without changing workflow logic.

#### Scenario: Branch push triggers build
- **WHEN** a commit is pushed to any branch
- **THEN** all matrix build jobs run

#### Scenario: Branch build skips push when push_enabled=false
- **WHEN** `push_enabled` is `false` and a branch build completes
- **THEN** no `docker push` or `docker manifest push` is executed

#### Scenario: Branch build pushes and runs manifest when push_enabled=true
- **WHEN** `push_enabled` is `true` and a branch build completes
- **THEN** per-arch images are pushed and manifest assembly runs, identical to the daily build workflow

---

### Requirement: Tag-based workflow is removed
The `container_tags.yml` workflow SHALL be deleted. No build or publish pipeline SHALL be triggered by git tag pushes.

#### Scenario: Tag push produces no workflow run
- **WHEN** a git tag is pushed
- **THEN** no GitHub Actions workflow is triggered for this repository
