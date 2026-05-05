## ADDED Requirements

### Requirement: Mounted source browser navigates one level at a time
The system SHALL provide a mounted-source browser for evidence path selection
that starts from the mounted roots and reveals child entries only when the
operator explicitly navigates into a directory.

#### Scenario: Initial browser view shows only first-level entries
- **WHEN** an operator opens the mounted-source browser for a device primary
  evidence source
- **THEN** the system lists only files and directories that exist at the first
  level of the mounted roots visible to the runtime

#### Scenario: Operator enters a directory to inspect its contents
- **WHEN** an operator chooses to navigate into a directory shown in the
  browser
- **THEN** the system loads and displays only the direct children of that
  directory
- **AND** the interface preserves visible context of the current location

### Requirement: Existing selected path can be reopened in the browser
The system SHALL allow an already saved mounted path to be reopened in the
browser so the operator can inspect its location, keep it, or replace it.

#### Scenario: Edit form opens browser on existing saved path
- **WHEN** an operator edits a device or evidence record that already has a
  saved mounted path
- **THEN** the browser can resolve that path inside the mounted tree
- **AND** the operator can continue navigating from that location
