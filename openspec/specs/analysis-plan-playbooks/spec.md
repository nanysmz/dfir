# analysis-plan-playbooks Specification

## Purpose
TBD - created by archiving change taxonomy-and-analysis-plan-playbooks. Update Purpose after archive.
## Requirements
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

### Requirement: Structured analysis-plan actions
The system SHALL represent each analysis-plan action as structured executable
data instead of plain text only.

#### Scenario: Action stores executable structure
- **WHEN** an operator prepares an analysis plan
- **THEN** each action can record path scope, applicable file kinds, search
  criteria, expected outputs, and linked reusable technique

#### Scenario: Existing text actions remain compatible
- **WHEN** an older plan only has textual action descriptions
- **THEN** the system can still derive or preserve usable actions while moving
  toward the structured representation

### Requirement: AnalysisPlan playbooks can contain multiple scoped actions
The system SHALL allow one analysis plan to contain multiple actions, each with
its own technical scope and criteria.

#### Scenario: One requested point uses multiple folders or criteria
- **WHEN** a requested point requires checking different evidence areas
- **THEN** the same plan can include several actions with different folders,
  file types, or search rules

### Requirement: One analysis plan launches as one execution unit
The system SHALL preserve `AnalysisPlan` as the execution unit even when the
plan references multiple targets.

#### Scenario: Plan with multiple targets creates one execution
- **WHEN** an operator launches an analysis plan that contains multiple
  `analysis_targets`
- **THEN** the system creates one execution associated with that plan
- **AND** that execution records the combined scope used for the run

### Requirement: Ready-plan eligibility is explicit
The system SHALL define when an analysis plan is considered ready for manual
execution.

#### Scenario: Plan is eligible for batch execution
- **WHEN** an analysis plan belongs to the current case, has a reusable point,
  has one or more valid targets, is not omitted, and has no active execution
- **THEN** the plan is eligible for `Ejecutar planes listos`

#### Scenario: Completed and failed plans are excluded from automatic batch rerun
- **WHEN** an operator triggers the case-level batch execution action
- **THEN** plans that are already completed or failed are not relaunched by
  default
- **AND** those plans remain available for explicit manual `Reejecutar` or
  `Reintentar` actions
