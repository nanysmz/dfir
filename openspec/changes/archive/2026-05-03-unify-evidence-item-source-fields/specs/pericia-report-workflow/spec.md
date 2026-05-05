## MODIFIED Requirements

### Requirement: Evidence organization
The system SHALL organize evidence as part of the pericia and distinguish
original evidence from preserved derived artifacts.

#### Scenario: Register evidence item
- **WHEN** an analyst associates a device, image, extraction, or other evidence source to a pericia
- **THEN** the system stores that evidence item with identifying metadata, a canonical primary source, and its role in the case

#### Scenario: Register preserved derived artifact
- **WHEN** the analyst preserves extracted files, screenshots, reports, or sampled content derived from the analysis
- **THEN** the system stores those preserved outputs as artifacts linked to the originating evidence item and pericia
