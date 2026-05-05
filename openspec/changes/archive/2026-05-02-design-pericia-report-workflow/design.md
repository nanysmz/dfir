## Context

The project already has a dockerized runtime and an initial `pericia-points` domain that can define, execute, and persist findings for individual analysis strategies. What is still missing is the case-driven workflow that reflects real forensic practice: a technical report is produced in the context of a judicial request, multiple evidence devices are analyzed as part of the same pericia, each requested point must be answered from that evidence, and technical impossibility or partial analysis must also be documented as first-class outcomes.

Two real report examples and a curated CSV of point types make the next architectural step clearer. The reports show a stable narrative structure (`objeto`, `elementos ofrecidos`, `herramientas`, `metodologia`, `informacion obtenida`, `conclusiones`, and sometimes `evidencia`/`anexos`). The most variable section, `informacion obtenida`, is organized by device, while the judicial mandate is expressed as requested points for the case as a whole. The CSV shows that operational analysis also depends on a second layer: where to look (`SAM`, `Web History`, `Installed Programs`, `AppData`, `Papelera`, multimedia reports, and similar artifacts), not just what question is being asked.

This means the system now needs to bridge at least four views of the same work:

- the judicial case and its metadata
- the literal requested points from the mandate or office
- the evidence and device-by-device technical analysis
- the final technical report and its structured sections

## Goals / Non-Goals

**Goals:**

- Define a case-centered domain model for a forensic pericia and its source documents.
- Represent requested points from the judicial mandate separately from reusable analysis strategies.
- Model evidence items, device-level analysis results, preserved derived evidence, and technical limitations.
- Define how existing pericia-point execution feeds case-specific answers and final report sections.
- Support the report reality that `informacion obtenida` is organized by evidence device while `conclusiones` and requested-point tracking are case-wide.

**Non-Goals:**

- Implement final DOCX or PDF generation in this change.
- Lock in a single OCR, multimedia, or external forensic-vendor integration.
- Replace the current `pericia-points` execution model; this change builds on it.
- Fully solve evidentiary chain-of-custody, signatures, or court submission workflows.

## Decisions

1. Model `Pericia` as the top-level case object.

   The central object should be the pericia itself, not the individual `PericiaPoint`. A pericia carries judicial metadata, source documents, evidence, requested points, analysis status, and report artifacts. This matches the real reports, where everything is framed in a single judicial context. Alternative considered: keeping the current point-first model and attaching ad hoc metadata around it, which would make report composition and evidence grouping awkward.

2. Separate requested points from analysis strategies.

   A requested point is the literal question or mandate from the case; an analysis strategy is the operational plan used to answer it. This distinction is essential because one requested point can require several strategies, and the same reusable strategy can support many cases. Alternative considered: treating requested points and reusable pericia points as the same entity, which would blur judicial wording with operational implementation.

3. Add a per-device analysis layer between evidence and final conclusions.

   The reports consistently organize `informacion obtenida` by device or evidence item. The system should therefore model an analysis result for each evidence item, including technical status, findings, requested-point responses, limitations, and preserved output paths. Alternative considered: summarizing only at the case level, which would lose the device-by-device structure that the report relies on.

4. Treat technical impossibility and partial analysis as first-class outcomes.

   Device outcomes cannot be limited to positive/negative findings. The domain must support states such as not acquired, partially analyzed, inaccessible, or pending specialized recovery, with supporting notes and recommendations. Alternative considered: storing only generic errors, which would not reflect the legal and technical meaning of those outcomes in the final report.

5. Compose the report from structured sections rather than a single generated blob.

   The final report should be modeled as a composition of sections that can combine reusable templates, structured evidence summaries, and analyst-authored narrative. This better matches the stable section layout seen in the reports and allows progressive automation without forcing full automatic drafting. Alternative considered: generating a single freeform report body directly from findings, which would be hard to review and maintain.

6. Reuse `pericia-points` as a lower-level execution capability inside the case workflow.

   The current `PericiaPoint`, `PericiaExecution`, and `PericiaFinding` model remains useful, but it should become a supporting execution layer for case-specific analysis plans and report responses. Alternative considered: replacing the existing capability entirely, which would throw away working execution primitives and duplicate concepts.

## Risks / Trade-offs

- [Model sprawl] -> Keep a clear distinction between case objects, requested points, analysis plans, and findings so the domain does not collapse into one oversized model.
- [Too much automation too early] -> Treat report drafting as assisted composition, not a fully automatic black box.
- [Evidence storage ambiguity] -> Explicitly model original evidence, working copies, and derived artifacts even if the first implementation uses simple filesystem paths.
- [Point catalog drift] -> Use the CSV-derived strategy catalog as templates, but keep case-level overrides so the system does not force a rigid one-size-fits-all workflow.
- [Mixed successful and failed device outcomes] -> Model per-device status separately from case-wide completion so one broken disk does not block the entire pericia record.

## Migration Plan

This is a forward design change. Implementation should likely proceed in stages:

1. Introduce the new case-centered models and relationships without removing existing `pericia-points` objects.
2. Add workflows for creating a pericia, registering source documents, and storing requested points.
3. Add evidence-item and per-device analysis entities that can reference existing pericia-point executions.
4. Add response and report-section models to assemble report-ready outputs.
5. Migrate admin/UI flows so analysts work from a pericia case rather than directly from reusable points.

Rollback would mean keeping the existing `pericia-points` capability available independently while disabling unfinished case/report workflows.

## Open Questions

- Should requested points be captured only manually at first, or should the system also support assisted extraction from OCR/text source documents?
- Should the first implementation support one evidence storage mode (reference only) or explicitly allow both reference and working-copy preservation modes?
- How much of the report narrative should be prefilled from structured data versus edited manually by the analyst?
- Should the system expose both “by device” and “by requested point” report views from the start, or only the device-oriented flow used in `informacion obtenida`?
