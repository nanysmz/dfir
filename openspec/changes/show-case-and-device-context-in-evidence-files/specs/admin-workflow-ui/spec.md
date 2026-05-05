## ADDED Requirements

### Requirement: Evidence file admin exposes case and device summaries
The system SHALL expose operator-readable case and device summaries in the
`Archivos de evidencia` admin workflow.

#### Scenario: Evidence file list shows readable summaries
- **WHEN** an operator opens the evidence-file list
- **THEN** each row shows enough summary context to understand the associated
  pericia and device labels without relying only on `Source path`

#### Scenario: Evidence file detail clarifies shared or missing associations
- **WHEN** an operator opens the detail page of an evidence file
- **THEN** the admin explains whether the file belongs to one device, multiple
  devices, or no current pericia association
