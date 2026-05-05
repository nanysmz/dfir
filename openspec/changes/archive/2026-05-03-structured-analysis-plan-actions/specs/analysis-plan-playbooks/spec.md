## ADDED Requirements

### Requirement: Structured analysis-plan actions
The system SHALL represent each analysis-plan action as structured executable
data instead of plain text only.

#### Scenario: Action stores executable structure
- **WHEN** an operator prepares an analysis plan
- **THEN** each action can record path scope, applicable file kinds, search
  criteria, expected outputs, and linked reusable technique

#### Scenario: Existing text actions remain compatible
- **WHEN** an older plan only has textual action descriptions
- **THEN** the system can still derive or preserve usable actions while moving
  toward the structured representation

### Requirement: AnalysisPlan playbooks can contain multiple scoped actions
The system SHALL allow one analysis plan to contain multiple actions, each with
its own technical scope and criteria.

#### Scenario: One requested point uses multiple folders or criteria
- **WHEN** a requested point requires checking different evidence areas
- **THEN** the same plan can include several actions with different folders,
  file types, or search rules
