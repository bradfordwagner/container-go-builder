## MODIFIED Requirements

### Requirement: Daily cron workflow always builds and pushes
A GitHub Actions workflow SHALL run daily at 7am EST (12:00 UTC, cron `0 12 * * *`) on the default branch (`main`) and execute the full `os × arch × go_version` build matrix. It SHALL always push images and assemble manifests — `push_enabled` in `config.yaml` is ignored by this workflow.

#### Scenario: Workflow triggers on schedule
- **WHEN** the cron schedule fires (daily)
- **THEN** the full matrix build, push, and manifest assembly runs automatically on the default branch

#### Scenario: workflow_dispatch allows triggering on any branch
- **WHEN** a user manually triggers the workflow via `workflow_dispatch` and selects a feature branch
- **THEN** the daily build runs against that branch's code, enabling testing without a cron on main

#### Scenario: Cron always pushes regardless of push_enabled
- **WHEN** the cron workflow runs and `push_enabled: false` in `config.yaml`
- **THEN** images are still pushed and manifests assembled
