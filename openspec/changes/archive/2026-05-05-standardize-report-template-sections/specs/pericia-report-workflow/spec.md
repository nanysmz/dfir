## MODIFIED Requirements

### Requirement: Report section composition
The system SHALL represent the technical report as structured sections that
combine stable templates and case-specific content, and it SHALL treat report
assembly as a distinct guided stage of the pericia, and it SHALL initialize
new pericias with a standard section structure based on the institutional
report model.

#### Scenario: Compose report sections
- **WHEN** the analyst prepares the technical report
- **THEN** the system supports at least sections for object, offered elements,
  tools, methodology, obtained information, and conclusions

#### Scenario: Populate obtained-information section
- **WHEN** the report includes the obtained-information section
- **THEN** the system can populate it from device-by-device analysis results
  while preserving analyst review and editing

#### Scenario: Report stage indicates completion readiness
- **WHEN** the workflow reaches report assembly
- **THEN** the system can determine whether the minimum report structure exists
  to consider the pericia ready for final review or closure

#### Scenario: New case starts with standard report structure
- **WHEN** a new pericia case is created
- **THEN** the report workflow starts with a predefined section structure that
  includes `Objeto`, `Elementos ofrecidos`, `Herramientas`, `Metodología`,
  `Información obtenida`, `Conclusiones`, `Evidencia`, and `Anexo`
- **AND** the operator can complete each section with case-specific content
