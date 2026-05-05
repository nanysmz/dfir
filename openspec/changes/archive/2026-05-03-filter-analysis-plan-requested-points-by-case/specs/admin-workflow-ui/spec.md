## MODIFIED Requirements

### Requirement: Existing admin workflows remain functional
The system SHALL preserve the current CRUD workflow for cases, evidence,
analysis, and report objects while adopting the new theme, and it SHALL add
contextual guidance inside the case workflow without breaking direct access to
those objects.

#### Scenario: Existing domain admin pages still work
- **WHEN** an operator opens list and detail pages for the current domain models
- **THEN** the themed admin continues to allow browsing, creating, editing, and
  linking those objects

#### Scenario: Case detail provides guided next actions
- **WHEN** an operator opens a pericia case detail page
- **THEN** the admin shows contextual progress, missing prerequisites, and the
  next recommended actions for continuing that specific case

#### Scenario: Analysis-plan form avoids unrelated requested points
- **WHEN** an operator selects a case in the analysis-plan admin form
- **THEN** the requested-point control does not present unrelated points from
  other pericias
