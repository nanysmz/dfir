## MODIFIED Requirements

### Requirement: Punto de pericia definition
The system SHALL model a punto de pericia as a configurable analysis definition with a name, type, parameters, scope, and execution rules, and it SHALL position that definition as a reusable technical technique that can participate in case-specific analysis playbooks rather than as the direct equivalent of the judicial requested point.

#### Scenario: Define an email search point
- **WHEN** an analyst configures a pericia point to search for an email address or domain
- **THEN** the system stores the point as a reusable definition with the selected type and matching parameters

#### Scenario: Define a keyword search point
- **WHEN** an analyst configures a pericia point to search for one or more keywords in textual evidence
- **THEN** the system stores the search terms and matching mode as part of the point definition

#### Scenario: Define an image characteristic point
- **WHEN** an analyst configures a pericia point to detect an image characteristic such as persons or nudity threshold
- **THEN** the system stores the detection target and confidence threshold as part of the point definition

#### Scenario: Reusable technique participates in a case playbook
- **WHEN** a case-level analysis plan is built for a requested point
- **THEN** the reusable pericia-point definition can be invoked as one action within that broader plan without replacing the requested-point record itself
