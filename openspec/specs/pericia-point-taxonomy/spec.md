# pericia-point-taxonomy Specification

## Purpose
TBD - created by archiving change taxonomy-and-analysis-plan-playbooks. Update Purpose after archive.
## Requirements
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

### Requirement: Taxonomy groups provide concrete starter actions
The system SHALL map taxonomy groups and recurring requested points to concrete
starter actions that analysts can review and refine.

#### Scenario: Catalog point suggests operational action
- **WHEN** a requested point matches a known recurring point from the catalog
- **THEN** the system can propose concrete folders, file types, and search
  criteria rather than only a broad family label

### Requirement: Recurring catalog covers concrete analysis examples
The system SHALL include concrete structured action examples for several
recurring requested points from the standard catalog.

#### Scenario: P2P installed point proposes concrete action
- **WHEN** the analyst plans `Identificación de programas P2P instalados`
- **THEN** the system can propose searching `ActividadReciente`, limiting to
  `html`, and using P2P-related keywords as the search criteria

