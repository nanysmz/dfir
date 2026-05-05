## Why

The Django admin is now the primary operational interface for managing pericias, evidence, analysis, and report assembly, but its current presentation is still generic and fragmented. Adopting a richer admin theme now will make the case-driven workflow easier to navigate, reduce operator friction, and give the domain grouping work a clearer visual structure.

## What Changes

- Adopt the `Unfold` admin theme for the Django backoffice.
- Replace the default admin presentation with a navigation structure aligned to the current domain split: casos periciales, evidencia, analisis, and informe.
- Configure branding, labels, icons, and menu organization so the admin reflects the DFIR workflow instead of raw Django model names.
- Preserve compatibility with the current Spanish locale, Argentina timezone defaults, and existing admin registrations.
- Add a small set of workflow-oriented admin improvements that make the primary pericia flow easier to start from the backoffice homepage.

## Capabilities

### New Capabilities
- `admin-workflow-ui`: A themed and workflow-oriented Django admin experience for operating the DFIR system.

### Modified Capabilities
- None.

## Impact

- Affected code: Django settings, admin configuration, domain admin modules, templates/static customization, and documentation.
- Dependencies: adds the `Unfold` package and any required configuration for Django admin integration.
- Systems: Django admin UI becomes the supported operational interface for the current workflow.
