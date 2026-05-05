## ADDED Requirements

### Requirement: Analysis stage exposes a clear manual start point
The system SHALL make the analysis stage of a case visibly startable without
requiring automatic execution on plan save.

#### Scenario: Case can begin analysis after planning
- **WHEN** a case already has evidence and one or more executable analysis
  plans
- **THEN** the workflow surfaces expose a clear action to begin analysis
  manually for that case
- **AND** the workflow does not require auto-execution during plan creation to
  indicate the next step

### Requirement: Analysis stage advances through ready plans and executions
The system SHALL treat the analysis stage as a transition from ready plans to
executions and then to result review.

#### Scenario: Ready plans do not yet imply active analysis
- **WHEN** a case has plans that are `Listos` but none has been launched
- **THEN** the workflow shows that analysis can begin but has not yet advanced
  into active execution

#### Scenario: Active or completed executions move the workflow forward
- **WHEN** one or more plans have pending, running, completed, or completed
  with observations executions
- **THEN** the workflow can use that state to guide the operator toward
  execution follow-up and result review before report drafting

### Requirement: Partial-but-useful executions remain valid workflow outputs
The system SHALL distinguish useful partial execution outcomes from total
execution failures.

#### Scenario: Execution completes with warnings
- **WHEN** an execution finishes and produces useful results together with file
  failures, unsupported items, or other relevant observations
- **THEN** the workflow can treat that execution as `Completado con
  observaciones`
- **AND** the case can still progress to evidence review and requested-point
  responses with analyst judgment

#### Scenario: Execution fails as a whole
- **WHEN** an execution cannot produce a technically useful result as a unit
- **THEN** the workflow treats it as `Fallido`
- **AND** the operator is guided toward retrying or adjusting the plan instead
  of assuming the analysis step is complete
