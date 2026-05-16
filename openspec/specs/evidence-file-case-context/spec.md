# evidence-file-case-context Specification

## Purpose
TBD - created by archiving change show-case-and-device-context-in-evidence-files. Update Purpose after archive.
## Requirements
### Requirement: Evidence file list shows pericia context
The system SHALL present each evidence file in the admin with visible pericia
context derived from the evidence items that reference that file.

#### Scenario: File linked to one case shows its pericia reference
- **WHEN** an operator reviews an evidence file linked through one or more
  evidence items to a single `PericiaCase`
- **THEN** the list or detail view shows that pericia reference in a visible
  operator-facing form

#### Scenario: File without linked case is identified as unassociated
- **WHEN** an evidence file has no linked evidence items
- **THEN** the admin indicates that it has no visible pericia association
  instead of leaving the context ambiguous

### Requirement: Evidence file shows associated devices
The system SHALL show which evidence items or devices are associated with each
evidence file.

#### Scenario: File linked to one device shows device label
- **WHEN** an evidence file is associated to one evidence item
- **THEN** the admin shows that device or evidence-item label alongside the
  file context

#### Scenario: File linked to multiple devices shows shared context
- **WHEN** an evidence file is associated to more than one evidence item
- **THEN** the admin indicates that multiple devices share that file
- **AND** the operator can identify the associated labels without opening
  unrelated records first

