## MODIFIED Requirements

### Requirement: Execution record
The system SHALL create an execution record for each run of a pericia point over a selected evidence scope, and it SHALL allow that execution to be associated with a case-specific analysis context.

#### Scenario: Record execution summary
- **WHEN** a pericia point is executed
- **THEN** the system stores execution metadata including analyzed files, unsupported files, failed files, and total findings

#### Scenario: Associate execution with case workflow
- **WHEN** a reusable pericia point is executed as part of a pericia case and requested-point response workflow
- **THEN** the system can associate that execution with the relevant case-specific analysis context without losing the reusable point definition

### Requirement: Report-ready traceability
The system SHALL retain enough metadata for findings to be cited later in technical reports and connected to case-specific responses.

#### Scenario: Trace a finding to source evidence
- **WHEN** a finding is reviewed for report generation
- **THEN** the system can identify the pericia point, execution, source file, extracted context, and matching metadata used to produce it

#### Scenario: Trace a finding into requested-point response
- **WHEN** a case-level response is prepared for a requested point
- **THEN** the system can associate the underlying finding with the requested point, evidence context, and report-oriented response that cites it
