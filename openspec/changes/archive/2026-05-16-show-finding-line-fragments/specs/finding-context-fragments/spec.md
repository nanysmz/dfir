## ADDED Requirements

### Requirement: Textual findings preserve line-based context fragments
The system SHALL preserve a structured line-based fragment for textual findings
so the operator can review the matched line together with nearby lines.

#### Scenario: Text matcher stores surrounding lines
- **WHEN** a textual match is detected in normalized content
- **THEN** the finding stores the matched value
- **AND** it stores a structured fragment with the matched line and
  approximately ten lines before and after when available

#### Scenario: Beginning or end of file limits fragment size
- **WHEN** the finding occurs near the beginning or end of the text
- **THEN** the system stores the available surrounding lines without requiring a
  full ten lines on each side

### Requirement: Findings keep backward-compatible fallback context
The system SHALL remain able to present findings that do not yet have
structured line fragments.

#### Scenario: Legacy finding only has short context
- **WHEN** an older finding lacks structured fragment data
- **THEN** the system still exposes the stored short context instead of failing

#### Scenario: Non-text finding lacks line semantics
- **WHEN** a finding comes from image labels, OCR, or another source without a
  reliable line model
- **THEN** the system does not require a line-based fragment to preserve the
  finding
