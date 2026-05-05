## ADDED Requirements

### Requirement: Pericia-point executions expose operational status
The system SHALL make pericia-point execution state visible beyond the final
finding set so that guided workflows can report operational progress.

#### Scenario: Execution exposes intermediate state
- **WHEN** a pericia-point run is dispatched and still processing evidence
- **THEN** the execution record exposes a state that indicates it is not yet
  complete

#### Scenario: Execution exposes progress summary
- **WHEN** a pericia-point run has partial or final processing counters
- **THEN** the execution record can expose progress-oriented summary data for
  use in the admin workflow
