## MODIFIED Requirements

### Requirement: Workflow-aligned navigation
The system SHALL expose admin navigation grouped by the current operational domains: casos periciales, evidencia, analisis, and informe, and it SHALL use that navigation to support a recommended case workflow.

#### Scenario: Domain groups are visible
- **WHEN** an operator opens the admin navigation
- **THEN** the available model entries are presented under domain-oriented groups rather than a single generic DFIR app block

#### Scenario: Group labels match workflow language
- **WHEN** an operator reads the admin navigation
- **THEN** the visible group names use workflow-oriented labels that match the pericia process in Spanish

#### Scenario: Navigation reinforces recommended order
- **WHEN** an operator uses the backoffice to move through a pericia
- **THEN** the navigation labels and module entry points reflect the recommended operational sequence of the case workflow

### Requirement: Backoffice entry point supports the pericia workflow
The system SHALL provide an admin home experience that helps an operator start or resume the main pericia workflow, and it SHALL expose progress, blockers, and next actions for guided execution.

#### Scenario: Operator can start from admin home
- **WHEN** an operator lands on `/admin/`
- **THEN** the admin home exposes clear access to the main workflow areas needed to create or continue a pericia

#### Scenario: Operator can resume a case from admin home
- **WHEN** an operator returns to the backoffice with pericias already in progress
- **THEN** the admin home can direct the operator toward the next recommended workflow step instead of only showing generic shortcuts

#### Scenario: Home shows workflow guidance
- **WHEN** an operator reviews the admin home
- **THEN** the interface shows the recommended stages of the pericia, their dependency order, and actionable entry points to continue the flow

### Requirement: Existing admin workflows remain functional
The system SHALL preserve the current CRUD workflow for cases, evidence, analysis, and report objects while adopting the new theme, and it SHALL add contextual guidance inside the case workflow without breaking direct access to those objects.

#### Scenario: Existing domain admin pages still work
- **WHEN** an operator opens list and detail pages for the current domain models
- **THEN** the themed admin continues to allow browsing, creating, editing, and linking those objects

#### Scenario: Case detail provides guided next actions
- **WHEN** an operator opens a pericia case detail page
- **THEN** the admin shows contextual progress, missing prerequisites, and the next recommended actions for continuing that specific case
