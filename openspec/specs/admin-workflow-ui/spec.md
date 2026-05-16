## Purpose
Definir los comportamientos y convenciones operativas de la interfaz de
administración usada para guiar el workflow pericial y evitar ambigüedades en
las superficies del backoffice.
## Requirements
### Requirement: Evidence admin distinguishes homonymous records across contexts
The system SHALL make it visible in the admin when evidence files or folders
share the same name but belong to different pericias or devices.

#### Scenario: List view distinguishes same-name evidence from different cases
- **WHEN** an operator reviews evidence records that share the same visible
  name
- **THEN** the admin shows enough pericia or device context to distinguish them
  as separate evidence records

#### Scenario: Detail view avoids ambiguous identity by name
- **WHEN** an operator opens a homonymous evidence record
- **THEN** the admin clarifies the current pericia/device context so the record
  is not interpreted as interchangeable with another same-name record

### Requirement: Finding admin shows readable contextual fragments
The system SHALL show a readable contextual fragment for each finding in admin
surfaces that inspect findings.

#### Scenario: Matched line is highlighted in finding detail
- **WHEN** an operator opens a textual finding with structured fragment data
- **THEN** the admin shows the surrounding fragment
- **AND** it visually distinguishes the line where the match occurred

#### Scenario: Operator can review nearby lines without leaving the finding
- **WHEN** a fragment is available for a finding
- **THEN** the admin shows enough nearby lines to interpret the match in place
  without reopening the source file

#### Scenario: Fallback context is shown when fragment is unavailable
- **WHEN** a finding has no structured line fragment
- **THEN** the admin shows the stored short context as a compatibility fallback

### Requirement: Evidence file admin exposes case and device summaries
The system SHALL expose operator-readable case and device summaries in the
`Archivos de evidencia` admin workflow.

#### Scenario: Evidence file list shows readable summaries
- **WHEN** an operator opens the evidence-file list
- **THEN** each row shows enough summary context to understand the associated
  pericia and device labels without relying only on `Source path`

#### Scenario: Evidence file detail clarifies shared or missing associations
- **WHEN** an operator opens the detail page of an evidence file
- **THEN** the admin explains whether the file belongs to one device, multiple
  devices, or no current pericia association

### Requirement: Existing admin workflows remain functional
The system SHALL preserve the current CRUD workflow for cases, evidence,
analysis, and report objects while adopting the new theme, and it SHALL add
contextual guidance inside the case workflow without breaking direct access to
those objects.

#### Scenario: Existing domain admin pages still work
- **WHEN** an operator opens list and detail pages for the current domain models
- **THEN** the themed admin continues to allow browsing, creating, editing, and
  linking those objects

#### Scenario: Case detail provides guided next actions
- **WHEN** an operator opens a pericia case detail page
- **THEN** the admin shows contextual progress, missing prerequisites, and the
  next recommended actions for continuing that specific case

#### Scenario: Guided device seed avoids duplicating existing evidence items
- **WHEN** an operator triggers the guided device-template seed on a case that
  already has one or more evidence items
- **THEN** the admin does not create additional seeded devices and instead
  shows a warning that the case must be completed from the existing evidence
  entries

#### Scenario: Case inline requested points keep case-local ordering clear
- **WHEN** an operator creates or edits requested points inside a pericia case
- **THEN** the admin presents those rows as belonging only to the current case
- **AND** it keeps the `order` field aligned to that case-local sequence instead
  of surfacing a generic uniqueness failure

### Requirement: Locale and timezone defaults remain consistent
The system SHALL preserve the current Spanish and Argentina-oriented admin behavior after theme adoption, and it SHALL keep the visible workflow language of the main operator surfaces aligned with `es-ar` and `America/Argentina/Buenos_Aires`.

#### Scenario: Theme respects locale configuration
- **WHEN** an operator uses the themed admin
- **THEN** the interface continues to use the configured `es-ar` language and `America/Argentina/Buenos_Aires` timezone defaults

#### Scenario: Analysis workflow labels are operator-facing Spanish
- **WHEN** an operator navigates the main `Analisis` surfaces of the backoffice
- **THEN** labels, help texts, and workflow guidance are shown in Spanish rather than a mixed English-Spanish vocabulary

### Requirement: Analysis workflow reflects playbook planning
The system SHALL present the analysis workflow in a way that makes it clear the
operator is building executable action playbooks for each requested point, and
it SHALL explain how the visible analysis surfaces fit together in a
recommended operational order.

#### Scenario: Operator sees requested point translated into actions
- **WHEN** an operator prepares analysis for a requested point
- **THEN** the admin workflow communicates that the plan represents concrete
  analysis actions derived from that point

#### Scenario: Operator can distinguish point, plan, and technique
- **WHEN** the operator navigates the analysis module
- **THEN** the interface avoids presenting the judicial requested point, the
  plan, and the reusable technique as if they were the same object

#### Scenario: Analysis module exposes recommended order
- **WHEN** an operator opens the analysis module without prior project context
- **THEN** the admin makes visible the recommended sequence between catalog
  techniques, case plans, executions, and review outputs

### Requirement: Evidence item form separates primary source from associated sources
The system SHALL present the `EvidenceItem` admin form with a clear source
management block that distinguishes the device's primary source from its
additional associated sources.

#### Scenario: Operator sees editable source roles
- **WHEN** an operator opens the evidence-item form
- **THEN** the interface shows an editable primary source and a separate
  editable area for associated sources of the same device

#### Scenario: Operator can replace source without ambiguity
- **WHEN** an operator changes the primary source or an associated source
- **THEN** the form makes clear which source is the canonical one used for the
  device and which ones are complementary

### Requirement: Evidence item form keeps derived evidence visually secondary
The system SHALL present `archivos de evidencia` as a resolved result of source
management rather than as the place where the operator defines the device's
main source.

#### Scenario: Resolved files appear as derived set
- **WHEN** an operator reviews the `EvidenceItem` form after selecting a
  primary source
- **THEN** the `archivos de evidencia` block is presented as derived linked
  evidence associated with that source

#### Scenario: Validation error points to source-management controls
- **WHEN** a primary or associated source is invalid during save
- **THEN** the form surfaces the validation failure in the source-management
  block instead of making the operator infer that the derived-evidence block is
  the actual source editor

