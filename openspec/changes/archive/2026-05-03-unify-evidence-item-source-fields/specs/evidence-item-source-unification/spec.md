## ADDED Requirements

### Requirement: Evidence item exposes a canonical primary source
The system SHALL present a single canonical primary source for an `EvidenceItem`
in the operator workflow, so the operator does not have to interpret multiple
fields that appear to represent the same origin.

#### Scenario: Operator sets primary device source
- **WHEN** an operator loads or edits an evidence item for a device
- **THEN** the workflow presents one primary source concept for that device

#### Scenario: Internal linking remains explicit
- **WHEN** the primary source is stored
- **THEN** the system still preserves explicit internal references for primary
  evidence and derived linked files

### Requirement: Derived evidence files follow the primary source
The system SHALL treat linked evidence files as a derivation of the selected
primary device source unless an explicitly supported advanced workflow says
otherwise.

#### Scenario: Folder source materializes linked files
- **WHEN** an operator selects a mounted device folder as the primary source
- **THEN** the system derives and links the corresponding evidence files from
  that folder

#### Scenario: Derived files are shown as resolved evidence
- **WHEN** linked files are presented in the admin
- **THEN** the interface makes it clear that they are the resolved evidence set
  associated with the primary source

### Requirement: Primary evidence reference can be simplified in the UI
The system SHALL allow the visible `Evidence file` field to be removed or
demoted from the main operator workflow if its role becomes redundant after
source unification.

#### Scenario: Redundant primary field is removed from main workflow
- **WHEN** the canonical source and derived evidence behaviors cover the
  operator workflow needs
- **THEN** the main evidence-item form no longer requires a separate visible
  `Evidence file` field
