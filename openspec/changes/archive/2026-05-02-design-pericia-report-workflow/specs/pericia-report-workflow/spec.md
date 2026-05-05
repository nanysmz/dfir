## ADDED Requirements

### Requirement: Pericia case record
The system SHALL model a forensic pericia as a case-level record that stores judicial metadata, source context, and report state.

#### Scenario: Create a pericia case
- **WHEN** an analyst registers a new forensic engagement
- **THEN** the system stores a pericia record with identifiers such as case reference, authority, dates, and analyst context

#### Scenario: Track pericia lifecycle
- **WHEN** a pericia progresses from intake through analysis and reporting
- **THEN** the system stores a case-level status that reflects the current stage of the pericia

### Requirement: Pericia source documents
The system SHALL store source documents related to the pericia, including the judicial request and future report artifacts.

#### Scenario: Register judicial request document
- **WHEN** an analyst attaches a mandate, office, or request document to a pericia
- **THEN** the system stores that document as a pericia source document with its type and extracted or transcribed text when available

#### Scenario: Distinguish request from report
- **WHEN** the system stores both incoming and outgoing documents for a pericia
- **THEN** it distinguishes at least judicial request documents from technical report documents

### Requirement: Requested points
The system SHALL model the requested points of the pericia separately from reusable analysis strategies.

#### Scenario: Capture literal requested point
- **WHEN** an analyst records a point requested by the authority
- **THEN** the system stores the literal text, order, and source document relationship for that requested point

#### Scenario: Track requested point status
- **WHEN** analysis progresses for a requested point
- **THEN** the system records whether that requested point is pending, in progress, answered, partially answered, or blocked by technical limitations

### Requirement: Analysis planning
The system SHALL support case-specific analysis planning that links requested points to operational analysis strategies.

#### Scenario: Associate strategies to a requested point
- **WHEN** an analyst prepares how to answer a requested point
- **THEN** the system allows one requested point to reference one or more operational strategies or reusable pericia-point definitions

#### Scenario: Preserve case-specific plan
- **WHEN** a reusable strategy is selected for a specific pericia
- **THEN** the system preserves the case-specific analysis plan separately from the reusable catalog definition

### Requirement: Evidence organization
The system SHALL organize evidence as part of the pericia and distinguish original evidence from preserved derived artifacts.

#### Scenario: Register evidence item
- **WHEN** an analyst associates a device, image, extraction, or other evidence source to a pericia
- **THEN** the system stores that evidence item with identifying metadata and its role in the case

#### Scenario: Register preserved derived artifact
- **WHEN** the analyst preserves extracted files, screenshots, reports, or sampled content derived from the analysis
- **THEN** the system stores those preserved outputs as artifacts linked to the originating evidence item and pericia

### Requirement: Device-by-device analysis record
The system SHALL store a technical analysis record for each relevant evidence item in the pericia.

#### Scenario: Record analysis by device
- **WHEN** an evidence item is analyzed as part of the case
- **THEN** the system stores a device-level analysis result associated with that evidence item and pericia

#### Scenario: Support information-obtained section structure
- **WHEN** the pericia report is assembled
- **THEN** the system can group analysis results by evidence item to populate the `informacion obtenida` section device by device

### Requirement: Technical limitation outcomes
The system SHALL record technical impossibility, partial access, or specialized-recovery outcomes as first-class analysis results.

#### Scenario: Device cannot be analyzed
- **WHEN** an evidence item cannot be acquired or analyzed because of missing power, hardware failure, or similar technical limitations
- **THEN** the system stores that outcome with the technical reason instead of treating it as a generic missing result

#### Scenario: Recommend follow-up action
- **WHEN** an analyst identifies a follow-up action such as obtaining a charger or using specialized recovery techniques
- **THEN** the system stores that recommendation with the affected evidence item or analysis result

### Requirement: Requested-point responses
The system SHALL store technical responses to requested points using evidence-backed results from the case.

#### Scenario: Answer requested point from multiple devices
- **WHEN** a requested point is informed by more than one evidence item
- **THEN** the system can aggregate evidence-backed results across those devices into a single requested-point response

#### Scenario: Preserve response rationale
- **WHEN** an analyst records a response for a requested point
- **THEN** the system stores the supporting evidence references, relevant findings, and technical rationale for that response

### Requirement: Report section composition
The system SHALL represent the technical report as structured sections that combine stable templates and case-specific content.

#### Scenario: Compose report sections
- **WHEN** the analyst prepares the technical report
- **THEN** the system supports at least sections for object, offered elements, tools, methodology, obtained information, and conclusions

#### Scenario: Populate obtained-information section
- **WHEN** the report includes the obtained-information section
- **THEN** the system can populate it from device-by-device analysis results while preserving analyst review and editing

### Requirement: Report-ready evidence traceability
The system SHALL preserve enough links between requested points, evidence, device-level analysis, findings, and preserved outputs to justify the final report.

#### Scenario: Trace report statement back to evidence
- **WHEN** a conclusion or requested-point response is reviewed
- **THEN** the system can identify the source evidence item, relevant analysis result, supporting finding, and preserved artifact path used to support that statement
