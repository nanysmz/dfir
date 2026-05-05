## ADDED Requirements

### Requirement: Evidence source paths support files and directories
The system SHALL allow admin operators to register an evidence source path as
either a regular file or a directory, as long as the path exists in the
filesystem visible to the dockerized runtime.

#### Scenario: Save evidence file with mounted directory
- **WHEN** an operator selects a directory path for an `EvidenceFile`
- **THEN** the admin accepts the path and stores it as a valid evidence source

#### Scenario: Save evidence file with regular file path
- **WHEN** an operator selects a regular file path for an `EvidenceFile`
- **THEN** the admin accepts the path and stores it as a valid evidence source

#### Scenario: Reject missing or unsupported path
- **WHEN** an operator submits an `EvidenceFile` path that does not exist or is
  neither a regular file nor a directory
- **THEN** the admin rejects the submission with a validation error

#### Scenario: Save evidence item with primary evidence path
- **WHEN** an operator selects a file or directory as the primary evidence
  source inside an `EvidenceItem`
- **THEN** the admin resolves or creates the corresponding `EvidenceFile` and
  links it to the evidence item during save

### Requirement: Evidence source autocomplete distinguishes path kinds
The system SHALL expose mounted-path suggestions for `EvidenceFile` that include
both directories and files, and it SHALL visually distinguish directories from
files in the suggestion list.

#### Scenario: Search mounted roots without query
- **WHEN** an operator focuses the `EvidenceFile` source-path field
- **THEN** the autocomplete can return both directory and file entries from the
  mounted evidence roots

#### Scenario: Directory suggestion is labeled
- **WHEN** a mounted directory is returned in autocomplete results
- **THEN** the result includes a directory-specific label that distinguishes it
  from file suggestions

### Requirement: Parent evidence hierarchy remains readable
The system SHALL label `Parent item` choices using enough mounted-path context
to show what evidence root or pericia branch each device belongs to.

#### Scenario: Parent item shows mounted root context
- **WHEN** an operator opens the `Parent item` selector for an evidence item
- **THEN** each option includes the relevant mounted-root or pericia context
  together with the device label
