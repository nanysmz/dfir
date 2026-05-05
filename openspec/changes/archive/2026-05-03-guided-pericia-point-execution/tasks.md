## 1. OpenSpec Sync

- [x] 1.1 Capture the current directory-based execution behavior in
  `pericia-points` and the new runner capability.
- [x] 1.2 Capture the admin-guided execution trigger in `admin-workflow-ui`.

## 2. Admin Trigger Design

- [x] 2.1 Choose the canonical button entry point: `AnalysisPlan`,
  `DeviceAnalysisResult`, or case guided actions.
- [x] 2.2 Define whether admin execution is synchronous, asynchronous, or dual
  mode, and how operator feedback is shown.

## 3. Implementation

- [x] 3.1 Add the guided admin action/button for executing pericia points from
  the selected workflow context.
- [x] 3.2 Connect the button to the existing execution service or Celery task
  with the correct case/device scope.
- [x] 3.3 Show execution outcome or link to resulting executions/findings after
  the action completes or is queued.

## 4. Verification

- [x] 4.1 Add admin tests covering visibility and behavior of the execution
  button.
- [x] 4.2 Verify the end-to-end execution flow in the dockerized runtime,
  including exported outputs under the expected hierarchy.
