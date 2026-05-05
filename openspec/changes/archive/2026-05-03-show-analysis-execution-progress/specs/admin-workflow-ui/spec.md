## ADDED Requirements

### Requirement: Analysis execution state is visible in the guided admin workflow
The system SHALL show analysis execution state and progress in the admin
workflow after analysis plans have been created.

#### Scenario: Plan view shows execution state
- **WHEN** an operator opens an analysis plan that has already been launched
- **THEN** the admin shows whether the analysis is pending, running, completed,
  or failed

#### Scenario: Guided case view shows analysis activity
- **WHEN** the current case is in the analysis stage
- **THEN** the guided admin surfaces expose whether executions are still in
  progress or ready for review
