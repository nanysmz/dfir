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

#### Scenario: Guided device seed avoids duplicating existing evidence items
- **WHEN** an operator triggers the guided device-template seed on a case that
  already has one or more evidence items
- **THEN** the admin does not create additional seeded devices and instead
  shows a warning that the case must be completed from the existing evidence
  entries
