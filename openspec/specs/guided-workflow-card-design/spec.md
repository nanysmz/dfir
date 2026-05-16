## Purpose
Definir la estructura visual y de contenido de las tarjetas guiadas del inicio
del admin para que el workflow pericial sea legible y accionable.

## Requirements

### Requirement: Guided workflow cards expose structured stage information
The system SHALL render each home-stage card with a stable information
structure that makes the workflow readable at a glance.

#### Scenario: Stage card exposes core hierarchy
- **WHEN** an operator reviews a workflow stage card on `/admin/`
- **THEN** the card shows at least the step label, stage title, short
  description, current state, and a primary action entry point

#### Scenario: Stage card exposes supporting guidance
- **WHEN** a stage depends on previous work or has a recommended context
- **THEN** the card shows a short supporting message with prerequisites,
  blockers, or operational guidance for that stage

### Requirement: Guided workflow cards differentiate visual state
The system SHALL visually distinguish stages that are ready, in progress,
blocked, or completed.

#### Scenario: Ready stage stands out as actionable
- **WHEN** a stage is the next recommended step and has no blockers
- **THEN** its card is rendered as immediately actionable with stronger CTA and
  emphasis than non-active stages

#### Scenario: Blocked stage exposes dependency state
- **WHEN** a stage cannot advance yet because prerequisites are missing
- **THEN** its card communicates that blocked state visually and includes a
  concise dependency message

#### Scenario: Completed stage remains visible without dominating
- **WHEN** a stage is already complete
- **THEN** its card remains visible for traceability while using lower emphasis
  than the currently actionable stage

### Requirement: Guided workflow cards remain responsive and theme-consistent
The system SHALL keep the redesigned stage cards compatible with the existing
Unfold admin theme and with small-screen layouts.

#### Scenario: Cards adapt to mobile stacking
- **WHEN** an operator opens the admin home on a narrow viewport
- **THEN** the stage cards remain readable, keep their hierarchy, and stack
  without overlapping or truncating critical guidance

#### Scenario: Cards use theme-consistent building blocks
- **WHEN** the cards are rendered inside the themed admin
- **THEN** they use the existing component and visual language of the current
  Unfold-based backoffice
