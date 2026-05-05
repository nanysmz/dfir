## ADDED Requirements

### Requirement: Derived evidence linkage preserves case and device context
The system SHALL preserve the originating pericia and evidence-item context
when linking derived evidence files from a primary source.

#### Scenario: Derived file from one case is not reused by homonymous name
- **WHEN** a primary source in one pericia produces a derived file whose name
  matches a file already seen in another pericia
- **THEN** the system does not reuse that other-case evidence record only by
  name coincidence

#### Scenario: Derived file keeps originating device traceability
- **WHEN** a derived evidence file is linked to an `EvidenceItem`
- **THEN** the system preserves which case and device originated that linkage
  even if similar names exist elsewhere
