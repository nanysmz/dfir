## ADDED Requirements

### Requirement: Analysis-plan requested-point selector follows the selected case
The system SHALL limit the `Requested point` choices in an `AnalysisPlan` form
to the requested points that belong to the currently selected `Pericia case`.

#### Scenario: New analysis plan shows only points from selected case
- **WHEN** an operator opens a new `AnalysisPlan` form with a selected
  `Pericia case`
- **THEN** the `Requested point` selector contains only points from that case

#### Scenario: Existing analysis plan preserves valid point visibility
- **WHEN** an operator opens an existing `AnalysisPlan`
- **THEN** the currently linked `Requested point` remains visible because it
  belongs to the same case as the plan

#### Scenario: Invalid cross-case points are not offered
- **WHEN** requested points from other pericias exist in the system
- **THEN** those points are not offered in the `Requested point` selector for
  the current plan case
