## MODIFIED Requirements

### Requirement: Analysis planning
The system SHALL support case-specific analysis planning that links requested
points to operational analysis strategies, and it SHALL make those plans part
of a guided sequence between evidence intake and report consolidation.

#### Scenario: Associate strategies to a requested point
- **WHEN** an analyst prepares how to answer a requested point
- **THEN** the system allows one requested point to reference one or more operational strategies or reusable pericia-point definitions

#### Scenario: Preserve case-specific plan
- **WHEN** a reusable strategy is selected for a specific pericia
- **THEN** the system preserves the case-specific analysis plan separately from the reusable catalog definition

#### Scenario: Plans unlock after evidence and requested points
- **WHEN** the workflow reaches the analysis-planning stage
- **THEN** the system can indicate whether the case is ready for planning based on prior completion of the prerequisite workflow stages

#### Scenario: Plan form offers only case-local requested points
- **WHEN** an operator edits or creates a plan for a given `Pericia case`
- **THEN** the requested-point selector only offers points that belong to that same case
