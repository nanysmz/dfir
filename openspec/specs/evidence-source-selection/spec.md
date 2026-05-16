## Purpose
Definir cómo se resuelven y validan rutas de evidencia seleccionadas por el
operador sin colapsar registros homónimos entre casos o dispositivos.
## Requirements
### Requirement: Evidence source resolution does not assume homonymous equivalence
The system SHALL resolve evidence sources without assuming that matching names
or similar visible folder structures imply the same evidence.

#### Scenario: Homonymous source is resolved within current case context
- **WHEN** an operator selects or saves a source path for evidence in the
  current pericia
- **THEN** the system resolves that source within the current evidence context
  instead of matching another record only by name similarity

#### Scenario: Repeated name across cases remains distinct at save time
- **WHEN** another pericia already contains an evidence file or folder with the
  same visible name
- **THEN** saving the current source does not merge or reuse that other-case
  record unless an explicitly supported identity rule confirms equivalence

### Requirement: Evidence source paths support files and directories
The system SHALL allow admin operators to register an evidence source path as
either a regular file or a directory, as long as the path exists in the
filesystem visible to the dockerized runtime, and it SHALL preserve editability
for already linked device sources even when the visible path uses mounted-path
aliases or is being corrected during a later edit.

#### Scenario: Save evidence file with mounted directory
- **WHEN** an operator selects a directory path for an `EvidenceFile`
- **THEN** the admin accepts the path and stores it as a valid evidence source

#### Scenario: Save evidence file with regular file path
- **WHEN** an operator selects a regular file path for an `EvidenceFile`
- **THEN** the admin accepts the path and stores it as a valid evidence source

#### Scenario: Reject missing or unsupported path
- **WHEN** an operator submits an `EvidenceFile` path that does not exist or is
  neither a regular file nor a directory
- **THEN** the admin rejects the submission with a validation error

#### Scenario: Save evidence item with primary evidence path
- **WHEN** an operator selects a file or directory as the primary evidence
  source inside an `EvidenceItem`
- **THEN** the admin resolves or creates the corresponding `EvidenceFile` and
  links it to the evidence item during save

#### Scenario: Reopen evidence item with already linked mounted alias
- **WHEN** an operator edits an `EvidenceItem` whose visible primary source is
  shown with a mounted alias such as `/evidence/input/...`
- **THEN** the admin accepts that source as valid if it resolves to the same
  configured runtime-visible path

#### Scenario: Replace primary source without clearing linked evidence manually
- **WHEN** an operator changes the primary source of an `EvidenceItem` from one
  valid file or directory to another valid file or directory
- **THEN** the admin saves the new primary source and recalculates the resolved
  primary evidence linkage without requiring manual cleanup of prior derived
  links

