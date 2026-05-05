## ADDED Requirements

### Requirement: Evidence admin distinguishes homonymous records across contexts
The system SHALL make it visible in the admin when evidence files or folders
share the same name but belong to different pericias or devices.

#### Scenario: List view distinguishes same-name evidence from different cases
- **WHEN** an operator reviews evidence records that share the same visible
  name
- **THEN** the admin shows enough pericia or device context to distinguish them
  as separate evidence records

#### Scenario: Detail view avoids ambiguous identity by name
- **WHEN** an operator opens a homonymous evidence record
- **THEN** the admin clarifies the current pericia/device context so the record
  is not interpreted as interchangeable with another same-name record
