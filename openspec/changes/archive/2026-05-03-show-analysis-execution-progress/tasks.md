## 1. Execution Status Model

- [x] 1.1 Review `PericiaExecution` and related task flow to identify the
  canonical states and progress data already available.
- [x] 1.2 Extend execution state/progress reporting where current signals are
  insufficient for operator-facing feedback.

## 2. Admin Visibility

- [x] 2.1 Show execution state and progress summary in `AnalysisPlan` admin.
- [x] 2.2 Surface analysis activity in the guided case workflow once plans have
  been launched.
- [x] 2.3 Distinguish not-started plans from running or completed executions in
  operator-facing copy and styling.

## 3. Verification

- [x] 3.1 Add tests covering execution status/progress visibility in admin and
  workflow summaries.
- [x] 3.2 Verify the behavior in the dockerized runtime.
