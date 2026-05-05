## ADDED Requirements

### Requirement: Case-aware pericia-point form
The system SHALL make the `Puntos de pericia` admin form aware of the selected
pericia context and it SHALL avoid showing irrelevant naming options from other
cases in the normal workflow.

#### Scenario: Form limits name options to the selected case
- **WHEN** an operator selects a `Pericia case` in the pericia-point admin form
- **THEN** the `Name` control shows only options relevant to that case

#### Scenario: Form refreshes options after changing case
- **WHEN** an operator changes the `Pericia case` inside the same form session
- **THEN** the `Name` control refreshes its available options to match the new
  case context
