## ADDED Requirements

### Requirement: Case workflow can seed pericia-point naming from requested points
The system SHALL allow the analysis workflow to bridge a pericia case's
requested points into the naming flow used when defining or refining a
`PericiaPoint`.

#### Scenario: Analyst creates strategy from case language
- **WHEN** an analyst defines a pericia-point strategy from within a case
- **THEN** the system can present names derived from that case's requested
  points instead of unrelated global options
