## 1. Case Context In PericiaPoint Form

- [x] 1.1 Add `Pericia case` context to the `PericiaPoint` admin workflow.
- [x] 1.2 Make the form resolve the active case correctly for both new and
  existing records.

## 2. Name Filtering

- [x] 2.1 Make `Name` show only case-relevant options when a pericia is
  selected.
- [x] 2.2 Preserve a valid fallback path when no pericia context is available.
- [x] 2.3 Refresh `Name` options if the operator changes the case in the same
  form session.

## 3. Verification

- [x] 3.1 Add tests covering case-based filtering in the `PericiaPoint` form.
- [x] 3.2 Add admin-view coverage for the guided case-aware behavior.
- [x] 3.3 Verify the behavior in the dockerized admin runtime.
