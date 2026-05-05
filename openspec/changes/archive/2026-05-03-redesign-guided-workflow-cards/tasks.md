## 1. Dashboard Card Structure

- [x] 1.1 Redefine the workflow card payload exposed by the admin dashboard context for visual state, helper text, and primary CTA
- [x] 1.2 Update the home template so stage cards read as an ordered guided sequence instead of equal-weight shortcuts
- [x] 1.3 Add visual differentiation for ready, in-progress, blocked, and completed stage cards using the current Unfold theme language

## 2. Home Layout Hierarchy

- [x] 2.1 Rebalance the `/admin/` layout so the step-by-step cards clearly answer how to start a pericia
- [x] 2.2 Refine the relation between the main workflow cards and the `Retomar pericias` block so start and resume paths do not compete
- [x] 2.3 Verify that the redesigned cards remain readable and correctly stacked on narrow viewports

## 3. Verification and Documentation

- [x] 3.1 Add or update admin tests that validate the new card hierarchy, status states, and key text on the home page
- [x] 3.2 Update operator-facing docs to describe the redesigned step-by-step cards and their intended usage
- [x] 3.3 Verify the redesigned home in the dockerized runtime before marking the change complete
