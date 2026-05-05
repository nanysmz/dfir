## ADDED Requirements

### Requirement: Themed admin experience
The system SHALL provide the Django admin through a configured `Unfold` theme instead of the default Django presentation.

#### Scenario: Admin loads with configured theme
- **WHEN** an authenticated operator opens `/admin/`
- **THEN** the admin is rendered using the configured `Unfold` integration for this project

### Requirement: Workflow-aligned navigation
The system SHALL expose admin navigation grouped by the current operational domains: casos periciales, evidencia, analisis, and informe.

#### Scenario: Domain groups are visible
- **WHEN** an operator opens the admin navigation
- **THEN** the available model entries are presented under domain-oriented groups rather than a single generic DFIR app block

#### Scenario: Group labels match workflow language
- **WHEN** an operator reads the admin navigation
- **THEN** the visible group names use workflow-oriented labels that match the pericia process in Spanish

### Requirement: Branded admin identity
The system SHALL configure admin branding so the interface reflects the DFIR application rather than default Django branding.

#### Scenario: Admin header reflects application identity
- **WHEN** an operator views the admin header or browser title
- **THEN** the interface displays configured product branding aligned to the DFIR system

### Requirement: Backoffice entry point supports the pericia workflow
The system SHALL provide an admin home experience that helps an operator start or resume the main pericia workflow.

#### Scenario: Operator can start from admin home
- **WHEN** an operator lands on `/admin/`
- **THEN** the admin home exposes clear access to the main workflow areas needed to create or continue a pericia

### Requirement: Existing admin workflows remain functional
The system SHALL preserve the current CRUD workflow for cases, evidence, analysis, and report objects while adopting the new theme.

#### Scenario: Existing domain admin pages still work
- **WHEN** an operator opens list and detail pages for the current domain models
- **THEN** the themed admin continues to allow browsing, creating, editing, and linking those objects

### Requirement: Locale and timezone defaults remain consistent
The system SHALL preserve the current Spanish and Argentina-oriented admin behavior after theme adoption.

#### Scenario: Theme respects locale configuration
- **WHEN** an operator uses the themed admin
- **THEN** the interface continues to use the configured `es-ar` language and `America/Argentina/Buenos_Aires` timezone defaults
