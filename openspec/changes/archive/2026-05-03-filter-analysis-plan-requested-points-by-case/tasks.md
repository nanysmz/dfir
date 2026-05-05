## 1. Form Filtering

- [x] 1.1 Make `AnalysisPlanAdminForm` derive the `requested_point` queryset
  from the selected `pericia_case`.
- [x] 1.2 Preserve correct filtering for both new forms and existing plans.

## 2. Operator UX

- [x] 2.1 Ensure the `Requested point` selector no longer shows points from
  other pericias in the normal admin workflow.
- [x] 2.2 Evaluate whether the selector also needs dynamic refresh when the
  case changes in the same form session.

## 3. Verification

- [x] 3.1 Add tests covering case-based filtering in the analysis-plan form.
- [x] 3.2 Verify the behavior in the dockerized admin runtime before closing
  the change.
