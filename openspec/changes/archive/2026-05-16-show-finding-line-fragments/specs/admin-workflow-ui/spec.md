## ADDED Requirements

### Requirement: Finding admin shows readable contextual fragments
The system SHALL show a readable contextual fragment for each finding in admin
surfaces that inspect findings.

#### Scenario: Matched line is highlighted in finding detail
- **WHEN** an operator opens a textual finding with structured fragment data
- **THEN** the admin shows the surrounding fragment
- **AND** it visually distinguishes the line where the match occurred

#### Scenario: Operator can review nearby lines without leaving the finding
- **WHEN** a fragment is available for a finding
- **THEN** the admin shows enough nearby lines to interpret the match in place
  without reopening the source file

#### Scenario: Fallback context is shown when fragment is unavailable
- **WHEN** a finding has no structured line fragment
- **THEN** the admin shows the stored short context as a compatibility fallback
