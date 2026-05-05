## 1. Case-Centered Domain

- [x] 1.1 Define Django models for pericia cases, source documents, requested points, evidence items, and preserved artifacts
- [x] 1.2 Add status fields for case lifecycle, requested-point progress, and device-level technical outcomes
- [x] 1.3 Model the relationship between original evidence, working copies, and derived artifacts used in the report

## 2. Analysis Planning and Execution Context

- [x] 2.1 Define case-specific analysis-plan entities that link requested points to reusable pericia-point strategies
- [x] 2.2 Extend pericia-point execution so runs can be associated with a pericia case and a requested-point response context
- [x] 2.3 Model device-by-device analysis results for the `informacion obtenida` section
- [x] 2.4 Model technical limitation outcomes and follow-up recommendations for non-analyzable devices

## 3. Report-Oriented Responses

- [x] 3.1 Define response entities that aggregate findings and technical observations into answers for requested points
- [x] 3.2 Define a structured report-section model covering object, offered elements, tools, methodology, obtained information, conclusions, and optional evidence/anexos
- [x] 3.3 Ensure responses and report sections can trace back to evidence items, findings, and preserved artifacts

## 4. Analyst Workflow

- [x] 4.1 Design the workflow for creating a new pericia and attaching judicial request documents
- [x] 4.2 Design the workflow for recording requested points from the mandate and mapping them to analysis strategies
- [x] 4.3 Design the workflow for reviewing results by device and by requested point before drafting conclusions
- [x] 4.4 Design the workflow for assembling and reviewing the final technical report

## 5. Verification and Documentation

- [x] 5.1 Add tests for case, requested-point, evidence, and analysis-plan model validation
- [x] 5.2 Add tests for linking pericia-point executions into case-specific report responses
- [x] 5.3 Add tests for technical-limitation outcomes and preserved-artifact traceability
- [x] 5.4 Document the pericia report workflow, the relationship between requested points and reusable analysis strategies, and the structure of `informacion obtenida`
