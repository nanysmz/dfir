## 1. Domain Model

- [x] 1.1 Define Django models for pericia point definitions, executions, and findings
- [x] 1.2 Add structured fields for point type, parameters, scope, and matching mode
- [x] 1.3 Add execution summary fields for analyzed, unsupported, failed, and matched files
- [x] 1.4 Add finding fields for source file, matched value, context, confidence, and engine metadata

## 2. Extraction Pipeline

- [x] 2.1 Define extractor interfaces for normalized text and normalized image outputs
- [x] 2.2 Implement the initial extraction flow for plain text and HTML files
- [x] 2.3 Implement placeholder extraction adapters for PDF and office documents with explicit unsupported/error reporting where needed
- [x] 2.4 Define the image extraction contract for labels, scores, detections, and OCR-ready extension points

## 3. Initial Point Families

- [x] 3.1 Implement the text email search point family with exact, domain, or equivalent configurable matching modes
- [x] 3.2 Implement the text keyword search point family with configurable term lists and matching modes
- [x] 3.3 Implement the image characteristic detection point family with configurable target labels and confidence thresholds
- [x] 3.4 Ensure point matching runs against normalized content instead of raw file parsing inside the matcher

## 4. Execution and Traceability

- [x] 4.1 Add a service layer or Celery task flow to execute a pericia point over selected evidence files
- [x] 4.2 Record immutable execution records and findings for each run
- [x] 4.3 Record unsupported files and extraction failures distinctly from successful findings
- [x] 4.4 Preserve enough metadata for each finding to be cited later in technical reports

## 5. Verification and Documentation

- [x] 5.1 Add tests for pericia point creation and validation by point family
- [x] 5.2 Add tests for text normalization and matcher behavior across multiple formats
- [x] 5.3 Add tests for execution summaries covering success, unsupported files, and extraction failures
- [x] 5.4 Document the pericia point model, initial point families, and future extension points for OCR and richer image analysis
