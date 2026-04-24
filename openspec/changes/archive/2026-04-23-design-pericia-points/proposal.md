## Why

The DFIR platform needs a formal model for "puntos de pericia" before implementing real analysis workflows. Defining pericia points now will let the system execute repeatable searches across heterogeneous evidence files and produce traceable findings that can later feed technical reports.

## What Changes

- Define the concept of a punto de pericia as a configurable analysis rule attached to evidence processing.
- Introduce an initial capability for text and image-oriented pericia points, including email search, keyword search, and image characteristic detection.
- Define a normalized extraction pipeline so searches operate on extracted content rather than file formats directly.
- Define a findings model that records matches, context, confidence, source file, and execution metadata.
- Establish the contract between pericia point execution and future report generation workflows.

## Capabilities

### New Capabilities

- `pericia-points`: Covers pericia point definitions, supported initial point types, extraction pipeline contracts, findings, and execution results.

### Modified Capabilities

- None.

## Impact

- Adds a new domain model for configurable analysis points and their execution results.
- Shapes future Django models, Celery jobs, extractors, and reporting workflows.
- Defines required behavior for text extraction, image classification, OCR-adjacent expansion paths, and result traceability.
- Establishes the first analysis-layer contract beyond runtime orchestration.
