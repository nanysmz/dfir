# pericia-point-case-scoped-name-selection Specification

## Purpose
TBD - created by archiving change filter-pericia-point-names-by-case. Update Purpose after archive.
## Requirements
### Requirement: Case-scoped pericia-point name selection
The system SHALL allow the pericia-point admin workflow to derive the visible
`Name` options from a selected `Pericia case`.

#### Scenario: Load names from the selected pericia
- **WHEN** an operator opens or creates a pericia point with a `Pericia case`
  selected
- **THEN** the system shows only name options associated with that pericia

#### Scenario: Keep fallback when no pericia is selected
- **WHEN** the operator uses the pericia-point form without an active pericia
  context
- **THEN** the system preserves a valid fallback path for naming the point

