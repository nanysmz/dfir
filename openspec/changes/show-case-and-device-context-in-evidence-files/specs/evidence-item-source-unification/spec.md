## ADDED Requirements

### Requirement: Derived evidence files remain traceable to source devices
The system SHALL present derived evidence files with visible traceability back
to the evidence items that resolved them from a primary source.

#### Scenario: Derived file shows originating device association
- **WHEN** an operator reviews a file that was linked automatically from an
  `EvidenceItem` primary source
- **THEN** the admin makes visible which evidence item or device produced that
  linkage

#### Scenario: Shared derived file shows more than one source device
- **WHEN** the same evidence file is linked from multiple evidence items
- **THEN** the admin does not collapse the context to a single device
- **AND** it communicates that the file is shared across associated devices
