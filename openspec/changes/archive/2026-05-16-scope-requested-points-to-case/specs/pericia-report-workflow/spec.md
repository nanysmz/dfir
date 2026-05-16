## MODIFIED Requirements

### Requirement: Requested points
The system SHALL model the requested points of the pericia separately from
reusable analysis strategies.

#### Scenario: Capture literal requested point
- **WHEN** an analyst records a point requested by the authority
- **THEN** the system stores the literal text, order, and source document
  relationship for that requested point
- **AND** that point remains scoped to the current pericia case only

#### Scenario: Track requested point status
- **WHEN** analysis progresses for a requested point
- **THEN** the system records whether that requested point is pending, in
  progress, answered, partially answered, or blocked by technical limitations

#### Scenario: Requested point order is unique within one case
- **WHEN** an operator records multiple requested points for the same pericia
- **THEN** the system preserves a unique `order` sequence within that case
- **AND** another pericia can reuse the same order values without conflict
