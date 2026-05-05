## ADDED Requirements

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
