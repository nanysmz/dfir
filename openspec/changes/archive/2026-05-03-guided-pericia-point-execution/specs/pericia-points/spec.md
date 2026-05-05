## MODIFIED Requirements

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
