# analysis-execution-progress-visibility Specification

## Purpose
TBD - created by archiving change show-analysis-execution-progress. Update Purpose after archive.
## Requirements
### Requirement: Visible analysis execution progress
The system SHALL expose visible execution state and progress for analysis runs
triggered from the pericia workflow.

#### Scenario: Operator sees that analysis is running
- **WHEN** an analysis execution has started but not finished yet
- **THEN** the system shows that the analysis is in progress instead of looking
  identical to a plan that never started

#### Scenario: Operator sees final execution outcome
- **WHEN** an analysis execution completes or fails
- **THEN** the system shows the resulting execution state and enough summary
  information to understand the outcome

