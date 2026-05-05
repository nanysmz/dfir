## ADDED Requirements

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
