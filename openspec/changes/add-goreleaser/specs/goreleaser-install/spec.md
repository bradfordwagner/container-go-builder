## ADDED Requirements

### Requirement: goreleaser is installed in the builder image
The builder image SHALL include the goreleaser binary at a pinned version via the `andrewrothstein.goreleaser` Ansible role.

#### Scenario: Binary is present after build
- **WHEN** the builder image is built for any supported os × arch combination
- **THEN** `goreleaser --version` exits 0 and reports the pinned version

#### Scenario: Version is pinned
- **WHEN** `goreleaser_version` is set in `playbook.yml`
- **THEN** the installed binary matches that exact version

### Requirement: goreleaser role is declared in requirements
The `requirements.yml` file SHALL declare `andrewrothstein.goreleaser` at a pinned role version so `ansible-galaxy` can install it reproducibly.

#### Scenario: Role installs without error
- **WHEN** `ansible-galaxy install -r requirements.yml` is executed
- **THEN** the `andrewrothstein.goreleaser` role is installed with no errors

### Requirement: goreleaser version is documented in README
The `README.md` SHALL include a table listing the installed goreleaser version so consumers know what version they get.

#### Scenario: Table is present
- **WHEN** a developer reads `README.md`
- **THEN** they can find the goreleaser version in the installed tools table without inspecting playbook files
