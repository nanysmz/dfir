## ADDED Requirements

### Requirement: Device primary evidence source selector shows navigation context
The system SHALL present the device primary evidence source selector with enough
navigation context for the operator to understand whether they are viewing the
mounted root or the contents of a nested directory.

#### Scenario: Operator sees current mounted location
- **WHEN** an operator is choosing a primary evidence source for a device
- **THEN** the interface shows the current mounted location being browsed
- **AND** it distinguishes that location from the final selected path value

#### Scenario: Operator can return to a parent location
- **WHEN** an operator has navigated into a subdirectory while choosing the
  primary evidence source
- **THEN** the interface provides a way to go back toward the mounted root
  without clearing the whole form
