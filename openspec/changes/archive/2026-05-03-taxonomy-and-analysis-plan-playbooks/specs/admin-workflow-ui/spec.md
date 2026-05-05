## ADDED Requirements

### Requirement: Analysis workflow reflects playbook planning
The system SHALL present the analysis workflow in a way that makes it clear the
operator is building executable action playbooks for each requested point.

#### Scenario: Operator sees requested point translated into actions
- **WHEN** an operator prepares analysis for a requested point
- **THEN** the admin workflow communicates that the plan represents concrete
  analysis actions derived from that point

#### Scenario: Operator can distinguish point, plan, and technique
- **WHEN** the operator navigates the analysis module
- **THEN** the interface avoids presenting the judicial requested point, the
  plan, and the reusable technique as if they were the same object
