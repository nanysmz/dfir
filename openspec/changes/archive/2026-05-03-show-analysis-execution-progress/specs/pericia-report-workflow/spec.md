## ADDED Requirements

### Requirement: Analysis stage distinguishes planning from execution progress
The system SHALL distinguish between analysis plans that merely exist and
analysis work that is actively running or already finished.

#### Scenario: Plans exist but execution has not started
- **WHEN** a case has analysis plans but no associated execution has started
- **THEN** the workflow does not present the analysis stage as already advanced
  through active execution

#### Scenario: Execution progress informs next workflow step
- **WHEN** one or more executions are running or have completed
- **THEN** the workflow can use that execution state to guide whether the case
  should keep analyzing or move toward responses and report drafting
