## Purpose
Definir el workflow case-driven de una pericia informatica, desde el ingreso
del caso hasta la respuesta por punto y el armado del informe tecnico final.
## Requirements
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
The system SHALL support case-specific analysis planning that links requested
points to operational analysis strategies, and it SHALL make those plans part
of a guided sequence between evidence intake and report consolidation.

#### Scenario: Associate strategies to a requested point
- **WHEN** an analyst prepares how to answer a requested point
- **THEN** the system allows one requested point to reference one or more operational strategies or reusable pericia-point definitions

#### Scenario: Preserve case-specific plan
- **WHEN** a reusable strategy is selected for a specific pericia
- **THEN** the system preserves the case-specific analysis plan separately from the reusable catalog definition

#### Scenario: Plans unlock after evidence and requested points
- **WHEN** the workflow reaches the analysis-planning stage
- **THEN** the system can indicate whether the case is ready for planning based on prior completion of the prerequisite workflow stages

#### Scenario: Plan form offers only case-local requested points
- **WHEN** an operator edits or creates a plan for a given `Pericia case`
- **THEN** the requested-point selector only offers points that belong to that same case

### Requirement: Evidence organization
The system SHALL organize evidence as part of the pericia and distinguish
original evidence from preserved derived artifacts.

#### Scenario: Register evidence item
- **WHEN** an analyst associates a device, image, extraction, or other evidence source to a pericia
- **THEN** the system stores that evidence item with identifying metadata, a canonical primary source, and its role in the case

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
The system SHALL represent the technical report as structured sections that
combine stable templates and case-specific content, and it SHALL treat report
assembly as a distinct guided stage of the pericia, and it SHALL initialize
new pericias with a standard section structure based on the institutional
report model.

#### Scenario: Compose report sections
- **WHEN** the analyst prepares the technical report
- **THEN** the system supports at least sections for object, offered elements, tools, methodology, obtained information, and conclusions

#### Scenario: Populate obtained-information section
- **WHEN** the report includes the obtained-information section
- **THEN** the system can populate it from device-by-device analysis results while preserving analyst review and editing

#### Scenario: Report stage indicates completion readiness
- **WHEN** the workflow reaches report assembly
- **THEN** the system can determine whether the minimum report structure exists to consider the pericia ready for final review or closure

#### Scenario: New case starts with standard report structure
- **WHEN** a new pericia case is created
- **THEN** the report workflow starts with a predefined section structure that
  includes `Objeto`, `Elementos ofrecidos`, `Herramientas`, `Metodología`,
  `Información obtenida`, `Conclusiones`, `Evidencia`, and `Anexo`
- **AND** the operator can complete each section with case-specific content

### Requirement: Report-ready evidence traceability
The system SHALL preserve enough links between requested points, evidence, device-level analysis, findings, and preserved outputs to justify the final report.

#### Scenario: Trace report statement back to evidence
- **WHEN** a conclusion or requested-point response is reviewed
- **THEN** the system can identify the source evidence item, relevant analysis result, supporting finding, and preserved artifact path used to support that statement

### Requirement: Workflow plans requested points through executable scoped actions
The system SHALL guide the analysis stage using scoped executable actions for
each requested point.

#### Scenario: Requested point becomes concrete action set
- **WHEN** the operator reaches the analysis-planning stage
- **THEN** the workflow can show not only that a plan exists, but also whether
  the requested point already has concrete actions with scope and criteria

### Requirement: Analysis stage distinguishes planning from execution progress
The system SHALL distinguish between analysis plans that merely exist and
analysis work that is actively running or already finished.

#### Scenario: Plans exist but execution has not started
- **WHEN** a case has analysis plans but no associated execution has started
- **THEN** the workflow does not present the analysis stage as already advanced
  through active execution

#### Scenario: Execution progress informs next workflow step
- **WHEN** one or more executions are running or have completed
- **THEN** the workflow can use that execution state to guide whether the case
  should keep analyzing or move toward responses and report drafting

### Requirement: Analysis stage exposes a clear manual start point
The system SHALL make the analysis stage of a case visibly startable without
requiring automatic execution on plan save.

#### Scenario: Case can begin analysis after planning
- **WHEN** a case already has evidence and one or more executable analysis
  plans
- **THEN** the workflow surfaces expose a clear action to begin analysis
  manually for that case
- **AND** the workflow does not require auto-execution during plan creation to
  indicate the next step

### Requirement: Analysis stage advances through ready plans and executions
The system SHALL treat the analysis stage as a transition from ready plans to
executions and then to result review.

#### Scenario: Ready plans do not yet imply active analysis
- **WHEN** a case has plans that are `Listos` but none has been launched
- **THEN** the workflow shows that analysis can begin but has not yet advanced
  into active execution

#### Scenario: Active or completed executions move the workflow forward
- **WHEN** one or more plans have pending, running, completed, or completed
  with observations executions
- **THEN** the workflow can use that state to guide the operator toward
  execution follow-up and result review before report drafting

### Requirement: Partial-but-useful executions remain valid workflow outputs
The system SHALL distinguish useful partial execution outcomes from total
execution failures.

#### Scenario: Execution completes with warnings
- **WHEN** an execution finishes and produces useful results together with file
  failures, unsupported items, or other relevant observations
- **THEN** the workflow can treat that execution as `Completado con
  observaciones`
- **AND** the case can still progress to evidence review and requested-point
  responses with analyst judgment

#### Scenario: Execution fails as a whole
- **WHEN** an execution cannot produce a technically useful result as a unit
- **THEN** the workflow treats it as `Fallido`
- **AND** the operator is guided toward retrying or adjusting the plan instead
  of assuming the analysis step is complete

### Requirement: Case workflow can seed pericia-point naming from requested points
The system SHALL allow the analysis workflow to bridge a pericia case's
requested points into the naming flow used when defining or refining a
`PericiaPoint`.

#### Scenario: Analyst creates strategy from case language
- **WHEN** an analyst defines a pericia-point strategy from within a case
- **THEN** the system can present names derived from that case's requested
  points instead of unrelated global options
