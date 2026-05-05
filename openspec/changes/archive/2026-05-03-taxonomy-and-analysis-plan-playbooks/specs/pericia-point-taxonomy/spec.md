## ADDED Requirements

### Requirement: Operational taxonomy for forensic requested points
The system SHALL define an operational taxonomy for recurring pericia requested
points so that analysis planning can classify them consistently.

#### Scenario: Taxonomy classifies a requested point
- **WHEN** an analyst registers or reviews a recurring requested point
- **THEN** the system can classify it into one or more operational analysis
  families instead of treating it as an unstructured free-form request

#### Scenario: Taxonomy covers the recurring catalog
- **WHEN** the system uses the standard catalog of 25 recurring requested points
- **THEN** each point has a defined place within the operational taxonomy

### Requirement: Taxonomy groups support analysis playbooks
The system SHALL allow each taxonomy group to suggest one or more reusable
analysis playbooks.

#### Scenario: Taxonomy group suggests a playbook
- **WHEN** a requested point belongs to a known taxonomy group
- **THEN** the system can suggest an appropriate family of executable analysis
  actions for planning
