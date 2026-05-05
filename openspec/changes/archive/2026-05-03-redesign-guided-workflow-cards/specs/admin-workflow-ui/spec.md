## MODIFIED Requirements

### Requirement: Backoffice entry point supports the pericia workflow
The system SHALL provide an admin home experience that helps an operator start
or resume the main pericia workflow, it SHALL expose progress, blockers, and
next actions for guided execution, and it SHALL present the main step-by-step
cards with a strong visual hierarchy that clarifies sequence and priority.

#### Scenario: Operator can start from admin home
- **WHEN** an operator lands on `/admin/`
- **THEN** the admin home exposes clear access to the main workflow areas
  needed to create or continue a pericia

#### Scenario: Operator can resume a case from admin home
- **WHEN** an operator returns to the backoffice with pericias already in progress
- **THEN** the admin home can direct the operator toward the next recommended
  workflow step instead of only showing generic shortcuts

#### Scenario: Home shows workflow guidance
- **WHEN** an operator reviews the admin home
- **THEN** the interface shows the recommended stages of the pericia, their
  dependency order, and actionable entry points to continue the flow

#### Scenario: Home cards emphasize sequence and next action
- **WHEN** an operator scans the step-by-step cards on the admin home
- **THEN** the interface visually distinguishes the next recommended stage from
  secondary or already completed stages

#### Scenario: Home cards expose blockers without hiding navigation
- **WHEN** a workflow stage is not ready because prerequisites are missing
- **THEN** the card communicates the blocker while still preserving direct
  navigation to the relevant admin surface
