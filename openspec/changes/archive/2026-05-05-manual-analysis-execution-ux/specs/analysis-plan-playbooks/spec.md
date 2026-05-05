## ADDED Requirements

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
