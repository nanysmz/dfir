## Purpose
Definir cómo un `EvidenceItem` mantiene una fuente primaria canónica y cómo se
preserva el contexto de caso y dispositivo al vincular evidencia derivada.
## Requirements
### Requirement: Evidence item exposes a canonical primary source
The system SHALL present a single canonical primary source for an `EvidenceItem`
in the operator workflow, so the operator does not have to interpret multiple
fields that appear to represent the same origin, and it SHALL allow that
primary source to be edited or replaced without losing explicit internal
references to the device's evidence set.

#### Scenario: Operator sets primary device source
- **WHEN** an operator loads or edits an evidence item for a device
- **THEN** the workflow presents one primary source concept for that device

#### Scenario: Internal linking remains explicit
- **WHEN** the primary source is stored
- **THEN** the system still preserves explicit internal references for primary
  evidence and derived linked files

#### Scenario: Operator changes canonical primary source
- **WHEN** an operator replaces the canonical source of an existing
  `EvidenceItem`
- **THEN** the system updates the canonical source projection for that device
  while preserving traceable linkage to the newly resolved primary evidence

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

### Requirement: Evidence item can track multiple associated sources
The system SHALL allow an `EvidenceItem` to keep one canonical primary source
and one or more additional associated sources that belong to the same device.

#### Scenario: Device stores primary and supporting sources
- **WHEN** an operator registers more than one source path for the same device
- **THEN** the system stores which source is primary and which sources are
  supporting associations of that `EvidenceItem`

#### Scenario: Operator edits associated source set
- **WHEN** an operator adds, edits, or removes a supporting source from a
  device
- **THEN** the system preserves the remaining source set without forcing the
  operator to recreate the canonical primary source

### Requirement: Derived evidence files follow the primary source
The system SHALL treat linked evidence files as a derivation of the selected
primary device source unless an explicitly supported advanced workflow says
otherwise, and it SHALL make clear that associated supporting sources do not
silently replace that canonical derivation rule.

#### Scenario: Folder source materializes linked files
- **WHEN** an operator selects a mounted device folder as the primary source
- **THEN** the system derives and links the corresponding evidence files from
  that folder

#### Scenario: Derived files are shown as resolved evidence
- **WHEN** linked files are presented in the admin
- **THEN** the interface makes it clear that they are the resolved evidence set
  associated with the primary source

#### Scenario: Supporting source does not implicitly replace primary derivation
- **WHEN** a device has additional associated sources besides the primary one
- **THEN** the system continues to derive the canonical resolved evidence set
  from the designated primary source unless the operator explicitly changes it

