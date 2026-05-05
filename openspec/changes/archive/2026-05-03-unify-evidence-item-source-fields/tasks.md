## 1. Source Model Consolidation

- [x] 1.1 Define which field becomes the canonical primary source for
  `EvidenceItem` in the operator workflow.
- [x] 1.2 Align `carpeta de evidencia del dispositivo` and `archivos de
  evidencia` so they behave as parts of the same primary-source flow.
- [x] 1.3 Preserve internal linking between the primary source,
  `evidence_file`, and derived `evidence_files`.

## 2. Evidence File Evaluation

- [x] 2.1 Decide whether `Evidence file` remains visible, becomes advanced, or
  is removed from the main form.
- [x] 2.2 Implement compatibility behavior for existing records that still rely
  on `evidence_file` as an explicit reference.

## 3. Admin UX

- [x] 3.1 Update the evidence-item form so the operator sees a unified source
  hierarchy instead of ambiguous duplicate entry points.
- [x] 3.2 Make the derived evidence-files section clearly reflect the resolved
  contents of the primary source.

## 4. Verification

- [x] 4.1 Add tests covering the unified operator flow and fallback behavior
  for existing data.
- [x] 4.2 Verify the evidence-item form behavior in the dockerized admin
  runtime before closing the change.
