## Purpose
Definir la plantilla estructural del informe técnico pericial con secciones
fijas, orden estable y edición por caso.

## Requirements
### Requirement: Pericia report template uses fixed section order
The system SHALL define a standard base template for the technical report of a
pericia and it SHALL preserve a stable section order for new cases.

#### Scenario: New pericia gets standard report sections
- **WHEN** an operator creates a new `PericiaCase`
- **THEN** the system provides report sections for `Objeto`, `Elementos
  ofrecidos`, `Herramientas`, `Metodología`, `Información obtenida`,
  `Conclusiones`, `Evidencia`, and `Anexo`
- **AND** those sections appear in that order unless the workflow explicitly
  supports an approved variation later

### Requirement: Standard report template remains editable by case
The system SHALL treat the standard report template as a reusable starting
structure, not as immutable final text.

#### Scenario: Analyst edits content of standard section
- **WHEN** an operator opens a standard report section for a specific case
- **THEN** the section content can be reviewed and edited for that case
- **AND** the case keeps the standard section identity and order
