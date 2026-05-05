## ADDED Requirements

### Requirement: Analysis admin provides visible manual execution entry points
The system SHALL make the start of manual analysis explicit in the admin UI at
both case level and plan level.

#### Scenario: Case view shows a primary action for ready plans
- **WHEN** an operator opens a pericia case with one or more analysis plans
  ready to run
- **THEN** the guided admin shows a visible action such as `Ejecutar planes
  listos`
- **AND** the interface summarizes how many plans are ready, active, failed, or
  completed for that case

#### Scenario: Plan list shows a direct action per row
- **WHEN** an operator reviews the analysis-plan list for a case
- **THEN** each plan row exposes a direct contextual action such as `Ejecutar
  este plan`, `Ver ejecucion`, `Reintentar`, or `Reejecutar`
- **AND** the action label reflects the latest known execution state

### Requirement: Analysis admin shows derived operator-facing plan states
The system SHALL present plan states in operator-facing language derived from
plan completeness and the latest related execution.

#### Scenario: Plan without required execution inputs appears incomplete
- **WHEN** an analysis plan lacks a reusable point, valid targets, or other
  minimum execution inputs
- **THEN** the admin can present the plan as `Incompleto` instead of implying
  that it is ready to run

#### Scenario: Ready plan appears as ready before first execution
- **WHEN** an analysis plan has valid targets and no active or completed
  execution yet
- **THEN** the admin can present the plan as `Listo`

#### Scenario: Latest execution refines visible plan state
- **WHEN** an analysis plan has a latest execution
- **THEN** the admin reflects visible states such as `En cola`, `En ejecucion`,
  `Completado`, `Completado con observaciones`, or `Fallido` according to that
  execution outcome

### Requirement: Manual batch execution reports what happened
The system SHALL summarize the effect of the case-level manual execution action.

#### Scenario: Batch action explains launched and omitted plans
- **WHEN** an operator triggers `Ejecutar planes listos`
- **THEN** the admin reports how many plans were launched
- **AND** it distinguishes plans omitted because they were incomplete, already
  active, omitted by status, or already completed
