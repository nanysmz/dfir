## ADDED Requirements

### Requirement: Requested points belong to exactly one pericia case
The system SHALL treat each `RequestedPoint` as data owned by one and only one
`PericiaCase`.

#### Scenario: New requested point is created within the active pericia
- **WHEN** an operator creates a requested point from a pericia case workflow
- **THEN** the system stores that point linked only to the current
  `PericiaCase`
- **AND** the operator does not need to resolve any cross-case context to save
  it

#### Scenario: Requested point ordering is local to the pericia
- **WHEN** two different pericias contain requested points with the same
  numeric `order`
- **THEN** the system treats those points as valid because their ordering is
  scoped independently per case

### Requirement: Requested point order is validated as a case-local sequence
The system SHALL validate `RequestedPoint.order` within the current pericia and
surface friendly case-local feedback before or during save.

#### Scenario: Inline creation suggests the next available order
- **WHEN** an operator adds a new requested point inside a case that already
  has existing requested points
- **THEN** the admin suggests the next available `order` for that pericia
  instead of defaulting to a value that collides with an existing point

#### Scenario: Duplicate order is explained in pericia language
- **WHEN** an operator tries to save two requested points with the same `order`
  inside one pericia
- **THEN** the system rejects the save
- **AND** it explains that the selected order is already used in that same
  pericia
