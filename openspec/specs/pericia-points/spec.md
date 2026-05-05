## Purpose
Definir los puntos de pericia reutilizables como tecnicas configurables,
ejecutables y trazables sobre evidencia normalizada, preservando su uso dentro
de workflows de caso.
## Requirements
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

### Requirement: Normalized extraction pipeline
The system SHALL process files through an extraction layer before applying
pericia matching logic.

#### Scenario: Textual file extraction
- **WHEN** the system processes a supported textual file such as HTML, TXT, PDF, or DOCX
- **THEN** it extracts normalized textual content and associated context metadata before running text-based pericia points

#### Scenario: Image file extraction
- **WHEN** the system processes a supported image file
- **THEN** it extracts normalized image analysis outputs such as labels, scores, detections, or OCR-derived text before running image-based pericia points

### Requirement: Format-independent matching
The system SHALL apply pericia matching logic against normalized content rather
than raw file formats.

#### Scenario: Keyword search across multiple formats
- **WHEN** the same keyword pericia point is executed over TXT, HTML, PDF, and DOCX evidence
- **THEN** the matching logic uses the normalized extracted text regardless of original file format

#### Scenario: Email search across generated forensic reports
- **WHEN** the same email pericia point is executed over generated HTML reports and document files
- **THEN** the matching logic operates over extracted content without format-specific point definitions

#### Scenario: Keyword search records multiple occurrences
- **WHEN** a keyword appears multiple times within the same analyzed file
- **THEN** the execution records each occurrence as a separate structured finding

### Requirement: Execution record
The system SHALL create an execution record for each run of a pericia point
over a selected evidence scope, and it SHALL allow that execution to be
associated with a case-specific analysis context.

#### Scenario: Record execution summary
- **WHEN** a pericia point is executed
- **THEN** the system stores execution metadata including analyzed files, unsupported files, failed files, and total findings

#### Scenario: Associate execution with case workflow
- **WHEN** a reusable pericia point is executed as part of a pericia case and requested-point response workflow
- **THEN** the system can associate that execution with the relevant case-specific analysis context without losing the reusable point definition

#### Scenario: Execute point from directory scope
- **WHEN** the selected evidence scope is a directory
- **THEN** the execution record preserves the original scope together with the expanded analyzed file set

### Requirement: Structured findings
The system SHALL store each match as a structured finding linked to its
pericia point, execution, and source file.

#### Scenario: Text finding with context
- **WHEN** a text-based pericia point finds a match
- **THEN** the finding stores the matched value, surrounding context, source file, and extraction metadata

#### Scenario: Image finding with confidence
- **WHEN** an image-based pericia point finds a relevant characteristic
- **THEN** the finding stores the detected label or score, confidence, source file, and engine metadata

#### Scenario: Finding keeps filesystem metadata
- **WHEN** a finding is recorded
- **THEN** its extraction metadata preserves the relevant source-file metadata and filesystem dates needed for later reporting

### Requirement: Unsupported and failed file reporting
The system SHALL distinguish successful analysis, unsupported formats, and extraction failures in execution results.

#### Scenario: Unsupported file format
- **WHEN** an execution encounters a file format with no supported extractor
- **THEN** the execution result records that file as unsupported instead of silently skipping it

#### Scenario: Extraction failure
- **WHEN** an extractor fails to process a supported file
- **THEN** the execution result records the failure separately from unsupported files and successful findings

### Requirement: Initial point families
The system SHALL support initial pericia point families for text email search, text keyword search, and image characteristic detection.

#### Scenario: Email point family
- **WHEN** an analyst selects the email search family
- **THEN** the system allows exact email, domain-based, or equivalent configurable text matching behavior

#### Scenario: Keyword point family
- **WHEN** an analyst selects the keyword search family
- **THEN** the system allows one or more search terms with a defined matching mode

#### Scenario: Image point family
- **WHEN** an analyst selects the image characteristic family
- **THEN** the system allows selecting at least one target characteristic and confidence threshold

### Requirement: Report-ready traceability
The system SHALL retain enough metadata for findings to be cited later in technical reports and connected to case-specific responses.

#### Scenario: Trace a finding to source evidence
- **WHEN** a finding is reviewed for report generation
- **THEN** the system can identify the pericia point, execution, source file, extracted context, and matching metadata used to produce it

#### Scenario: Trace a finding into requested-point response
- **WHEN** a case-level response is prepared for a requested point
- **THEN** the system can associate the underlying finding with the requested point, evidence context, and report-oriented response that cites it

### Requirement: Pericia-point executions expose operational status
The system SHALL make pericia-point execution state visible beyond the final
finding set so that guided workflows can report operational progress.

#### Scenario: Execution exposes intermediate state
- **WHEN** a pericia-point run is dispatched and still processing evidence
- **THEN** the execution record exposes a state that indicates it is not yet
  complete

#### Scenario: Execution exposes progress summary
- **WHEN** a pericia-point run has partial or final processing counters
- **THEN** the execution record can expose progress-oriented summary data for
  use in the admin workflow

