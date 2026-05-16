## MODIFIED Requirements

### Requirement: Evidence organization
The system SHALL organize evidence as part of the pericia and distinguish
original evidence from preserved derived artifacts, and it SHALL preserve
enough structured device-source and device-description metadata to support the
report's `elementos ofrecidos` section.

#### Scenario: Register evidence item
- **WHEN** an analyst associates a device, image, extraction, or other evidence source to a pericia
- **THEN** the system stores that evidence item with identifying metadata, a canonical primary source, and its role in the case

#### Scenario: Register preserved derived artifact
- **WHEN** the analyst preserves extracted files, screenshots, reports, or sampled content derived from the analysis
- **THEN** the system stores those preserved outputs as artifacts linked to the originating evidence item and pericia

#### Scenario: Device metadata can feed offered-elements narrative
- **WHEN** an operator records or updates the technical metadata of a device
- **THEN** the workflow keeps that metadata available in structured form for
  reuse in the report's `elementos ofrecidos` section

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

#### Scenario: Offered elements can reuse device description inputs
- **WHEN** the report workflow needs to draft the `elementos ofrecidos`
  section
- **THEN** the system can reuse the structured device description inputs stored
  on each `EvidenceItem`
