## ADDED Requirements

### Requirement: AnalysisPlan as requested-point playbook
The system SHALL treat `AnalysisPlan` as the case-specific playbook that
translates one requested point into one or more executable analysis actions.

#### Scenario: One requested point expands into multiple actions
- **WHEN** a requested point requires several technical checks to be answered
- **THEN** the associated analysis plan can contain multiple executable actions
  instead of only a single flat strategy link

#### Scenario: Plan stays tied to case context
- **WHEN** the operator prepares analysis for a requested point
- **THEN** the analysis plan remains tied to the pericia case, the requested
  point, and the selected evidence scope for those actions

### Requirement: Analysis actions can map to reusable techniques
The system SHALL allow analysis-plan actions to reference reusable
`PericiaPoint` techniques without equating the requested point itself to that
technique.

#### Scenario: Requested point uses reusable techniques
- **WHEN** a point about communications, fraud, malware, or chronology is
  planned
- **THEN** the plan can invoke one or more reusable techniques appropriate to
  that objective
