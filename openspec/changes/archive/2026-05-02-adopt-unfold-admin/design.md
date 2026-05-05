## Context

The project currently uses Django admin as the primary operator interface. The domain is already split into four logical apps (`dfir_cases`, `dfir_evidence`, `dfir_analysis`, and `dfir_reports`), but the admin experience still behaves like a lightly customized default Django admin. The next step is not a new product surface; it is a better operational shell around the workflow that already exists.

Adopting `Unfold` is a cross-cutting UI change because it touches dependency management, Django settings, admin registration patterns, navigation structure, visual branding, and the first screen an analyst sees when starting a pericia. The change should improve usability without forcing a rewrite of the underlying admin models or replacing the Django admin with a separate frontend.

## Goals / Non-Goals

**Goals:**

- Introduce `Unfold` as the supported admin theme for the project.
- Reflect the domain split in a clearer navigation model with grouped menu entries and labels aligned to the pericia workflow.
- Provide a more purposeful admin landing experience so operators can start a new pericia and move through the workflow with less hunting.
- Preserve compatibility with the current proxy-model strategy, locale defaults, and admin-driven workflow.
- Keep the initial implementation small enough to ship without redesigning every individual form.

**Non-Goals:**

- Building a separate custom frontend outside Django admin.
- Rewriting the data model or replacing proxy-model admin registration.
- Fully redesigning every admin form layout in the first pass.
- Automating report generation or changing case/report business rules.

## Decisions

1. Use `Unfold` as a thematic wrapper around the current admin, not as a pretext to replace it.

   The fastest path to a better operator experience is to keep Django admin as the control surface and layer `Unfold` on top. This preserves current models, permissions, and CRUD behavior while improving navigation and presentation. Alternative considered: building a separate application shell or dashboard, which would take longer and duplicate admin capabilities we are already using.

2. Keep the current domain split and map it directly into `Unfold` navigation.

   The recent app split already encodes the right mental model: casos periciales, evidencia, analisis, and informe. `Unfold` navigation should reinforce that structure with grouped menu entries, human labels, and icons. Alternative considered: leaving the menu entirely app-driven and only changing the theme, which would look better but still feel generic.

3. Introduce a workflow-oriented admin home configuration before deeper form redesigns.

   The first payoff should come from a clearer landing page and sidebar, not from trying to perfect every form at once. A useful first pass is branded navigation, quick links to the main domain areas, and consistent section titles. Alternative considered: immediately customizing all change forms and list views, which would increase scope and slow adoption.

4. Preserve the proxy-model approach for admin grouping.

   The new domain apps are already using proxy models to group the admin without moving the underlying tables. `Unfold` should build on that pattern instead of undoing it. Alternative considered: collapsing admin back into a single app or moving the concrete models themselves, both of which would create churn without helping the operator.

5. Treat branding and locale as part of the operator experience.

   The admin should reflect the DFIR product identity and preserve Spanish/Argentina defaults. That includes site title, headers, navigation labels, and any visible helper copy. Alternative considered: using `Unfold` with its defaults and only minimal configuration, which would leave the product feeling unfinished.

## Risks / Trade-offs

- [Theme integration drift] -> Keep the first pass close to documented `Unfold` configuration and avoid unnecessary overrides.
- [Visual improvement without workflow improvement] -> Prioritize menu structure, homepage links, and primary flow entry points over decorative changes.
- [Admin customization sprawl] -> Start with global theme config and a few high-value admin classes before touching every model admin.
- [Dependency compatibility] -> Pin the `Unfold` version and verify it against the current Django version in Dockerized tests.
- [Hidden regression in existing admin flows] -> Re-run admin checks and keep current CRUD registrations intact while layering theme features incrementally.

## Migration Plan

1. Add the `Unfold` dependency and register it in Django settings.
2. Configure global branding, menu grouping, icons, and site metadata for the admin.
3. Update domain admin classes to inherit from the appropriate `Unfold` admin base classes where needed.
4. Add a workflow-oriented landing configuration and ensure `/admin/` remains the operational entry point.
5. Verify the current CRUD paths for pericia cases, evidence, analysis, and report sections still work.

Rollback is straightforward: remove the `Unfold` dependency and settings, restore standard Django admin classes, and keep the existing domain split unchanged.

## Open Questions

- Which icon vocabulary should represent the four DFIR domains most clearly without over-decorating the admin?
- Do we want the first pass to include a custom dashboard widget set, or only grouped navigation and branding?
- Should the admin home emphasize “create pericia” as the primary call to action, or simply expose the grouped domain modules more clearly?
