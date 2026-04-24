## Context

The DFIR runtime skeleton is already in place, but the platform still lacks a domain model for the actual forensic questions it must answer. A "punto de pericia" needs to become a first-class concept so analysts can define what to search, execute it across evidence collections, and obtain structured findings suitable for technical reporting.

The initial problem space spans heterogeneous evidence files: generated HTML reports from forensic tools, plain text files, PDFs, office documents, and image files. Different formats require different extraction strategies, but the downstream pericia logic should not depend directly on file type. The system should support early point types like email search, keyword search, and image characteristic detection, while leaving room for OCR, entity extraction, and richer computer vision later.

This design must also preserve forensic traceability. Findings need to record where they came from, how they were extracted, and which pericia point produced them. That metadata is essential for future reporting and expert review.

## Goals / Non-Goals

**Goals:**

- Define a reusable domain model for pericia points, executions, normalized content, and findings.
- Support initial point types for email search, keyword search, and image characteristic detection.
- Separate file extraction from matching logic so multiple formats can feed the same pericia point type.
- Ensure findings are traceable to source files, extraction methods, and execution metadata.
- Leave clear extension points for OCR, additional file types, and more advanced analysis engines.

**Non-Goals:**

- Implement the full extraction stack for every file type in this change.
- Choose final OCR, NLP, or computer-vision vendors/models in this change.
- Build final report templates or user-facing analyst workflows in this change.
- Solve chain-of-custody, evidence hashing, or legal report formatting in full detail here.

## Decisions

1. Model pericia points as configurable analysis definitions, not hard-coded tasks.

   A pericia point should store a type, parameters, supported formats, and matching rules. This allows the same execution framework to handle "search for exact email", "search for domain", "match keywords", or "detect persons in images" by changing configuration rather than writing a new pipeline for each point. Alternatives considered: bespoke one-off Celery tasks per analysis type, which would make the system harder to extend and reason about.

2. Introduce a normalized extraction layer between files and matchers.

   The platform should first extract normalized content from each file, then run the pericia matcher against that normalized representation. For text-oriented points, normalized content will generally be extracted text plus context metadata such as page number, section, or source fragment. For image-oriented points, normalized content will be labels, scores, detections, and OCR text when available. Alternatives considered: making each pericia point parse raw files directly, which would duplicate extraction logic and blur responsibilities.

3. Separate pericia point type from execution engine.

   A point type like `text_keyword_search` or `image_detection` describes behavior at the domain level, while a lower-level engine or extractor identifies the implementation path used to process a given file. This makes it possible to evolve extraction engines independently from the user-facing pericia model. Alternatives considered: encoding implementation details directly into the point type, which would couple domain language too tightly to tools or libraries.

4. Treat findings as immutable, reportable records from a single execution.

   Each execution should produce findings that reference the pericia point, source file, extracted fragment or detection context, and confidence when relevant. Findings should not be mutated in place after execution; instead, rerunning a point should create a new execution record and new findings. Alternatives considered: continuously updating a single rolling result per point, which would weaken auditability.

5. Start with three first-class point families.

   The first supported families should be:
   - text email search
   - text keyword search
   - image characteristic detection

   These families cover the examples already identified and provide a practical slice across both text and image evidence. Alternatives considered: designing a highly abstract taxonomy first, which would add complexity without enough implementation pressure.

6. Make unsupported files explicit in execution results.

   Execution summaries should distinguish between analyzed files, unsupported files, extraction failures, and successful findings. This prevents silent gaps in pericial coverage. Alternatives considered: ignoring unsupported formats, which would create misleading confidence in the results.

## Risks / Trade-offs

- Text extraction quality varies by format -> Normalize around extractor output and preserve extractor metadata so later improvements do not require changing the pericia point contract.
- PDFs may be text-based or scanned -> Design the pipeline so OCR can be inserted later without changing point definitions.
- Keyword searches can produce many false positives -> Preserve context fragments and matching mode so analysts can review and refine points.
- Image detection confidence scores vary by model -> Store confidence and engine metadata with findings so thresholds remain auditable.
- Old office formats like `.doc` may need specialized tooling -> Report unsupported formats explicitly instead of pretending they were analyzed.
- The model may grow quickly across text, OCR, and vision -> Keep pericia point type, extractor, and finding concerns separated to avoid a tangled monolith.

## Migration Plan

This is a forward design change and introduces no required data migration yet. Implementation should add domain models and execution contracts incrementally, starting with the initial point families and a minimal execution summary. Existing runtime orchestration remains unchanged.

## Open Questions

- Should pericia points be reusable templates across cases, or always copied into a case-specific snapshot before execution?
- How much surrounding context should a text finding store by default: line, paragraph, page, or a bounded character window?
- Should image detections be stored as simple labels first, or include bounding boxes in the initial model?
- When OCR is added, should OCR be modeled as a separate extractor stage or as an image-specific engine within the same pipeline?
