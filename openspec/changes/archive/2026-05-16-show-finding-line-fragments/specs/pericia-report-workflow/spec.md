## ADDED Requirements

### Requirement: Finding traceability includes readable contextual fragment
The system SHALL preserve enough finding context to justify a report statement
with a readable fragment, not only the matched value.

#### Scenario: Exported finding includes structured fragment
- **WHEN** the system exports or preserves a finding-derived artifact
- **THEN** that output includes the matched value
- **AND** it includes the structured contextual fragment when available

#### Scenario: Report support can reference highlighted finding line
- **WHEN** an analyst reviews a finding to support a requested-point response or
  report section
- **THEN** the system can identify not only the source file but also the
  highlighted line and surrounding fragment that support the statement
