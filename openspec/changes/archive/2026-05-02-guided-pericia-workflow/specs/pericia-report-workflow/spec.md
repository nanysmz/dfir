## MODIFIED Requirements

### Requirement: Pericia case record
The system SHALL model a forensic pericia as a case-level record that stores judicial metadata, source context, and report state, and it SHALL expose enough workflow state to guide the operator step by step through the case lifecycle.

#### Scenario: Create a pericia case
- **WHEN** an analyst registers a new forensic engagement
- **THEN** the system stores a pericia record with identifiers such as case reference, authority, dates, and analyst context

#### Scenario: Track pericia lifecycle
- **WHEN** a pericia progresses from intake through analysis and reporting
- **THEN** the system stores a case-level status that reflects the current stage of the pericia

#### Scenario: Derive guided workflow progress
- **WHEN** the operator needs to continue a case
- **THEN** the system can determine the current workflow stage, completed stages, blocked stages, and next recommended stage from the case data already recorded

### Requirement: Analysis planning
The system SHALL support case-specific analysis planning that links requested points to operational analysis strategies, and it SHALL make those plans part of a guided sequence between evidence intake and report consolidation.

#### Scenario: Associate strategies to a requested point
- **WHEN** an analyst prepares how to answer a requested point
- **THEN** the system allows one requested point to reference one or more operational strategies or reusable pericia-point definitions

#### Scenario: Preserve case-specific plan
- **WHEN** a reusable strategy is selected for a specific pericia
- **THEN** the system preserves the case-specific analysis plan separately from the reusable catalog definition

#### Scenario: Plans unlock after evidence and requested points
- **WHEN** the workflow reaches the analysis-planning stage
- **THEN** the system can indicate whether the case is ready for planning based on prior completion of the prerequisite workflow stages

### Requirement: Requested-point responses
The system SHALL store technical responses to requested points using evidence-backed results from the case, and those responses SHALL participate in the guided completion logic of the pericia workflow.

#### Scenario: Answer requested point from multiple devices
- **WHEN** a requested point is informed by more than one evidence item
- **THEN** the system can aggregate evidence-backed results across those devices into a single requested-point response

#### Scenario: Preserve response rationale
- **WHEN** an analyst records a response for a requested point
- **THEN** the system stores the supporting evidence references, relevant findings, and technical rationale for that response

#### Scenario: Response stage can be evaluated for progress
- **WHEN** the operator needs to know whether the case is ready to move from technical analysis to report drafting
- **THEN** the system can evaluate whether requested-point responses are still pending, partially complete, blocked, or sufficiently complete to continue

### Requirement: Report section composition
The system SHALL represent the technical report as structured sections that combine stable templates and case-specific content, and it SHALL treat report assembly as a distinct guided stage of the pericia.

#### Scenario: Compose report sections
- **WHEN** the analyst prepares the technical report
- **THEN** the system supports at least sections for object, offered elements, tools, methodology, obtained information, and conclusions

#### Scenario: Populate obtained-information section
- **WHEN** the report includes the obtained-information section
- **THEN** the system can populate it from device-by-device analysis results while preserving analyst review and editing

#### Scenario: Report stage indicates completion readiness
- **WHEN** the workflow reaches report assembly
- **THEN** the system can determine whether the minimum report structure exists to consider the pericia ready for final review or closure
