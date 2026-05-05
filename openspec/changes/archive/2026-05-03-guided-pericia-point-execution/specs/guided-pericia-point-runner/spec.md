## ADDED Requirements

### Requirement: Guided pericia-point runner accepts directory scopes
The system SHALL allow a pericia-point execution to start from a file or from a
directory scope associated with the pericia, and it SHALL expand directory
scopes recursively into analyzable files.

#### Scenario: Run point over device directory
- **WHEN** an operator or workflow action executes a pericia point against a
  device directory
- **THEN** the system expands the directory recursively and analyzes each
  eligible file as part of the same execution

#### Scenario: Skip unsupported filesystem entries
- **WHEN** a directory contains hidden files, system trash, or non-file entries
- **THEN** the runner skips those entries instead of treating them as analysis
  failures

### Requirement: Guided runner exports match outputs by workflow hierarchy
The system SHALL export each preserved match result under the dockerized output
mount using a hierarchy based on pericia, device, point, and file type.

#### Scenario: Export match to output hierarchy
- **WHEN** a point execution finds a match in a case/device context
- **THEN** the system writes an output artifact under
  `nro_pericia/dispositivo/punto/tipoArchivo`

#### Scenario: Export includes source traceability
- **WHEN** a match is exported
- **THEN** the output contains the source file name, source folder, full path,
  metadata, and relevant filesystem dates

### Requirement: Guided runner preserves exported findings as artifacts
The system SHALL create preserved-artifact records for exported matches when
the execution is linked to a pericia case and evidence item.

#### Scenario: Exported match becomes preserved artifact
- **WHEN** an execution with case/device context exports a match
- **THEN** the system creates a `PreservedArtifact` linked to the originating
  finding and evidence item
