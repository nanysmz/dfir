## ADDED Requirements

### Requirement: Analysis admin exposes structured actions
The system SHALL present analysis-plan actions in the admin as structured
operator-facing units instead of only a free-form text area.

#### Scenario: Operator sees structured action inputs
- **WHEN** an operator edits an analysis plan
- **THEN** the interface makes visible the folder scope, file-kind scope, and
  search criteria for each action

#### Scenario: Operator understands what will be executed
- **WHEN** an operator reviews a plan before execution
- **THEN** the interface communicates clearly what each action will inspect and
  how it will search
