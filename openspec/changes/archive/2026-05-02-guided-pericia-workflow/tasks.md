## 1. Workflow Model

- [x] 1.1 Define the canonical guided stages of a pericia from case intake through final report review
- [x] 1.2 Define completion and blocking criteria for each stage using existing case, evidence, analysis, response, and report objects
- [x] 1.3 Add automated tests for stage derivation, next-step resolution, and blocked-state behavior

## 2. Shared Guidance Logic

- [x] 2.1 Implement a reusable workflow helper/service that computes progress, blockers, and next recommended actions for a case
- [x] 2.2 Expose helper outputs in a form consumable by both the admin dashboard and the per-case admin detail view
- [x] 2.3 Document how guided workflow state is derived from the existing domain model without adding redundant state

## 3. Guided Admin Experience

- [x] 3.1 Update the Unfold dashboard to show a step-by-step pericia flow with actionable entry points for start and resume
- [x] 3.2 Update `PericiaCaseAdmin` to show case-specific progress, unmet prerequisites, and next actions inside the guided workflow
- [x] 3.3 Add or refine admin actions, redirects, and contextual prompts so each step can advance naturally into the next one

## 4. End-to-End Verification

- [x] 4.1 Add server-side tests covering the guided dashboard and case-detail guidance states
- [x] 4.2 Add workflow tests for advancing through documents, requested points, evidence, plans, responses, and report sections in order
- [x] 4.3 Verify the guided flow in the dockerized runtime and update operator-facing docs for the final step-by-step experience
