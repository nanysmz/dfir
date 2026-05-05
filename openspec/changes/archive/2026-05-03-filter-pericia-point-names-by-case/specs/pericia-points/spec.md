## MODIFIED Requirements

### Requirement: Punto de pericia definition
The system SHALL model a punto de pericia as a configurable analysis definition with a name, type, parameters, scope, and execution rules, and it SHALL allow that definition to be initialized from a selected pericia context when the operator is working inside a specific case.

#### Scenario: Define an email search point
- **WHEN** an analyst configures a pericia point to search for an email address or domain
- **THEN** the system stores the point as a reusable definition with the selected type and matching parameters

#### Scenario: Define a keyword search point
- **WHEN** an analyst configures a pericia point to search for one or more keywords in textual evidence
- **THEN** the system stores the search terms and matching mode as part of the point definition

#### Scenario: Define an image characteristic point
- **WHEN** an analyst configures a pericia point to detect an image characteristic such as persons or nudity threshold
- **THEN** the system stores the detection target and confidence threshold as part of the point definition

#### Scenario: Initialize pericia-point name from case context
- **WHEN** an analyst creates a pericia point while a specific `Pericia case` is active
- **THEN** the system can derive the visible `Name` choices from that case instead of forcing an entirely global or free-text selection
