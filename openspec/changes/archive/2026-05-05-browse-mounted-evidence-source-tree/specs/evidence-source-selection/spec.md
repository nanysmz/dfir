## MODIFIED Requirements

### Requirement: Evidence source autocomplete distinguishes path kinds
The system SHALL expose mounted-path suggestions for `EvidenceFile` that include
both directories and files, and it SHALL visually distinguish directories from
files in the suggestion list, and it SHALL not surface deep descendant paths in
the initial device-source selection view unless the operator explicitly
navigates into a directory.

#### Scenario: Search mounted roots without query
- **WHEN** an operator focuses the `EvidenceFile` source-path field
- **THEN** the autocomplete can return both directory and file entries from the
  mounted evidence roots

#### Scenario: Directory suggestion is labeled
- **WHEN** a mounted directory is returned in autocomplete results
- **THEN** the result includes a directory-specific label that distinguishes it
  from file suggestions

#### Scenario: Device primary source starts from first-level mounted entries
- **WHEN** an operator opens the `fuente primaria de evidencia del dispositivo`
  selector without having navigated into any subdirectory
- **THEN** the visible choices only include first-level files and directories
  from the mounted roots
- **AND** deep descendant paths are excluded from that initial choice set
