## 1. Dependency and Global Configuration

- [x] 1.1 Add the `Unfold` dependency to the project and register it in Django settings
- [x] 1.2 Configure global admin branding, titles, and locale-safe theme settings
- [x] 1.3 Ensure the themed admin remains compatible with the current Dockerized runtime and Django version

## 2. Navigation and Domain Grouping

- [x] 2.1 Configure `Unfold` navigation to present casos periciales, evidencia, analisis, and informe as distinct workflow groups
- [x] 2.2 Assign clear labels and icons to the grouped admin navigation entries
- [x] 2.3 Keep the current proxy-model admin structure working under the themed navigation

## 3. Workflow Entry and Admin Integration

- [x] 3.1 Adapt the primary domain admin classes to the `Unfold` admin base classes where needed
- [x] 3.2 Configure the admin home or sidebar so operators can quickly start or resume a pericia workflow
- [x] 3.3 Verify that list, detail, inline, and relation-heavy admin pages remain usable with the new theme

## 4. Verification and Documentation

- [x] 4.1 Add tests covering theme configuration and grouped navigation expectations that can be asserted server-side
- [x] 4.2 Run Django checks and Dockerized test/lint verification after the admin theme integration
- [x] 4.3 Document how the themed admin is organized and how operators should use it as the backoffice entry point
