# device-offered-item-description Specification

## Purpose
TBD - created by archiving change fix-evidence-item-source-management. Update Purpose after archive.
## Requirements
### Requirement: Device description metadata is structured for report reuse
The system SHALL store technical device-description inputs in structured form so
they can be reused consistently across evidence intake and report assembly.

#### Scenario: Operator captures structured offered-item fields
- **WHEN** an operator registers or edits a device evidence item
- **THEN** the system allows structured capture of fields such as device class,
  interface, brand, model, serial number, and capacity

#### Scenario: Partial metadata remains valid
- **WHEN** only some technical fields are known for a device
- **THEN** the system stores the known values without requiring a complete
  offered-item description upfront

### Requirement: Offered-item description can be rendered from metadata
The system SHALL be able to render or suggest an offered-item narrative from
the structured metadata stored for a device.

#### Scenario: Storage device description is suggested from metadata
- **WHEN** a storage device has type, interface, brand, model, serial number,
  and capacity recorded
- **THEN** the system can produce or suggest a narrative equivalent to a
  formal `elementos ofrecidos` description for that device

#### Scenario: Edited metadata updates offered-item suggestion
- **WHEN** an operator corrects technical metadata such as model, serial
  number, or capacity
- **THEN** the offered-item description generated or suggested from that device
  reflects the updated values

