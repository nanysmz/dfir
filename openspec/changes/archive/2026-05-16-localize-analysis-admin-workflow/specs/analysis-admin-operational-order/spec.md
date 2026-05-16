## ADDED Requirements

### Requirement: Analysis admin exposes an operator-first execution order
The system SHALL explain the recommended working order of the analysis module
for operators running a pericia in the Buenos Aires workflow.

#### Scenario: Operator sees the four-step analysis order
- **WHEN** an operator opens the analysis module or one of its guided entry
  points
- **THEN** the system can communicate the recommended order as:
  `Puntos de pericia -> Planes de analisis -> Ejecuciones -> Resultados`

#### Scenario: Order clarifies responsibility of each object
- **WHEN** an operator reviews the recommended order
- **THEN** the system distinguishes the reusable technique catalog, the
  case-specific plan, the actual execution, and the technical result review

### Requirement: Analysis order remains aligned with case workflow
The system SHALL keep the analysis admin order consistent with the broader
guided case workflow.

#### Scenario: Analysis order matches case progression
- **WHEN** an operator enters analysis from a specific case
- **THEN** the recommended sequence shown in the analysis module is compatible
  with the case workflow stage that follows evidence registration and precedes
  report drafting
