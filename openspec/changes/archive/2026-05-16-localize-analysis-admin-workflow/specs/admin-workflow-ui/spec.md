## MODIFIED Requirements

### Requirement: Locale and timezone defaults remain consistent
The system SHALL preserve the current Spanish and Argentina-oriented admin behavior after theme adoption, and it SHALL keep the visible workflow language of the main operator surfaces aligned with `es-ar` and `America/Argentina/Buenos_Aires`.

#### Scenario: Theme respects locale configuration
- **WHEN** an operator uses the themed admin
- **THEN** the interface continues to use the configured `es-ar` language and `America/Argentina/Buenos_Aires` timezone defaults

#### Scenario: Analysis workflow labels are operator-facing Spanish
- **WHEN** an operator navigates the main `Analisis` surfaces of the backoffice
- **THEN** labels, help texts, and workflow guidance are shown in Spanish rather than a mixed English-Spanish vocabulary

### Requirement: Analysis workflow reflects playbook planning
The system SHALL present the analysis workflow in a way that makes it clear the
operator is building executable action playbooks for each requested point, and
it SHALL explain how the visible analysis surfaces fit together in a
recommended operational order.

#### Scenario: Operator sees requested point translated into actions
- **WHEN** an operator prepares analysis for a requested point
- **THEN** the admin workflow communicates that the plan represents concrete
  analysis actions derived from that point

#### Scenario: Operator can distinguish point, plan, and technique
- **WHEN** the operator navigates the analysis module
- **THEN** the interface avoids presenting the judicial requested point, the
  plan, and the reusable technique as if they were the same object

#### Scenario: Analysis module exposes recommended order
- **WHEN** an operator opens the analysis module without prior project context
- **THEN** the admin makes visible the recommended sequence between catalog
  techniques, case plans, executions, and review outputs
