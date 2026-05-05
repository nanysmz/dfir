## ADDED Requirements

### Requirement: Report admin shows standard section sequence
The system SHALL present report sections in the admin following the standard
pericia sequence so the operator can complete the report in a familiar order.

#### Scenario: Report tab shows expected section order
- **WHEN** an operator opens the report stage of a pericia
- **THEN** the visible section list follows the sequence `Objeto`, `Elementos
  ofrecidos`, `Herramientas`, `Metodología`, `Información obtenida`,
  `Conclusiones`, `Evidencia`, `Anexo`

#### Scenario: Operator distinguishes fixed section structure from editable content
- **WHEN** an operator edits the report from the admin
- **THEN** the interface makes clear that the section order comes from a
  standard template
- **AND** the textual content of each section remains editable for the current
  case
