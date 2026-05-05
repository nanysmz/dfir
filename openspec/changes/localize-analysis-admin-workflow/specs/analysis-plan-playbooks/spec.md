## MODIFIED Requirements

### Requirement: AnalysisPlan as requested-point playbook
The system SHALL treat `AnalysisPlan` as the case-specific playbook that
translates one requested point into one or more executable analysis actions,
and it SHALL let the operator define the mounted evidence locations that bound
where those actions run.

#### Scenario: One requested point expands into multiple actions
- **WHEN** a requested point requires several technical checks to be answered
- **THEN** the associated analysis plan can contain multiple executable actions
  instead of only a single flat strategy link

#### Scenario: Plan stays tied to case context
- **WHEN** the operator prepares analysis for a requested point
- **THEN** the analysis plan remains tied to the pericia case, the requested
  point, and the selected evidence scope for those actions

#### Scenario: Operator selects mounted analysis targets
- **WHEN** an operator edits a plan such as `Correos`
- **THEN** the `Analysis targets` control allows selecting one or more mounted
  folders or files as the scope of that plan

### Requirement: AnalysisPlan playbooks can contain multiple scoped actions
The system SHALL allow one analysis plan to contain multiple actions, each with
its own technical scope and criteria, and it SHALL keep the selected
`analysis_targets` visible as the global evidence scope of the plan.

#### Scenario: One requested point uses multiple folders or criteria
- **WHEN** a requested point requires checking different evidence areas
- **THEN** the same plan can include several actions with different folders,
  file types, or search rules

#### Scenario: Analysis targets remain editable after save
- **WHEN** an operator reopens an existing analysis plan
- **THEN** the previously selected target locations remain visible and can be
  changed without losing the rest of the playbook configuration
