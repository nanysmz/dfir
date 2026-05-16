## ADDED Requirements

### Requirement: Evidence item form separates primary source from associated sources
The system SHALL present the `EvidenceItem` admin form with a clear source
management block that distinguishes the device's primary source from its
additional associated sources.

#### Scenario: Operator sees editable source roles
- **WHEN** an operator opens the evidence-item form
- **THEN** the interface shows an editable primary source and a separate
  editable area for associated sources of the same device

#### Scenario: Operator can replace source without ambiguity
- **WHEN** an operator changes the primary source or an associated source
- **THEN** the form makes clear which source is the canonical one used for the
  device and which ones are complementary

### Requirement: Evidence item form keeps derived evidence visually secondary
The system SHALL present `archivos de evidencia` as a resolved result of source
management rather than as the place where the operator defines the device's
main source.

#### Scenario: Resolved files appear as derived set
- **WHEN** an operator reviews the `EvidenceItem` form after selecting a
  primary source
- **THEN** the `archivos de evidencia` block is presented as derived linked
  evidence associated with that source

#### Scenario: Validation error points to source-management controls
- **WHEN** a primary or associated source is invalid during save
- **THEN** the form surfaces the validation failure in the source-management
  block instead of making the operator infer that the derived-evidence block is
  the actual source editor
