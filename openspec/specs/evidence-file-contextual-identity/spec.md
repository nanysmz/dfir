## ADDED Requirements

### Requirement: Evidence file identity is not inferred from name alone
The system SHALL NOT treat two evidence files or folders as the same evidence
only because they share the same visible name or a similar apparent structure.

#### Scenario: Same file name appears in different pericias
- **WHEN** two different pericias contain evidence files or folders with the
  same visible name
- **THEN** the system treats them as distinct evidence unless an explicitly
  supported identity rule confirms equivalence

#### Scenario: Same folder name appears in different devices
- **WHEN** two devices linked to different pericias contain folders with the
  same visible name
- **THEN** the system preserves separate evidence identity and traceability for
  each folder context

### Requirement: Evidence identity can rely on contextual and verifiable signals
The system SHALL support evidence identity decisions using pericia context,
associated device context, and verifiable content signals when available.

#### Scenario: Content verification distinguishes homonymous files
- **WHEN** two evidence files have the same visible name but different
  verifiable content
- **THEN** the system does not collapse them into a single evidence identity

#### Scenario: Context preserves distinction when content verification is absent
- **WHEN** verifiable content is not yet available for two homonymous evidence
  records from different pericias or devices
- **THEN** the system still preserves them as distinct by context instead of
  assuming equivalence
