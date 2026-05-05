## Why

The DFIR platform can already define and execute individual pericia points, but it still lacks the case-driven workflow needed to produce a full technical report for a real forensic engagement. The recent report examples and point catalog make it clear that the product goal is not just extracting findings, but managing a pericia end to end: capturing the judicial request, organizing evidence, documenting device-by-device analysis, preserving derived evidence, and assembling a report-ready result.

## What Changes

- Introduce a case-driven pericia workflow centered on generating the technical forensic report.
- Add a domain model for the pericia case, source documents, requested points, evidence items, and analysis results by device.
- Define how requested points from the judicial mandate are translated into operational analysis strategies and linked to existing pericia point execution capabilities.
- Define report-ready response structures that connect findings, technical observations, limitations, preserved evidence, and conclusions.
- Define how the system records technical impossibility, partial analysis, and other non-success outcomes that still need to appear in the report.

## Capabilities

### New Capabilities
- `pericia-report-workflow`: Covers case metadata, judicial request documents, requested points, evidence organization, per-device analysis results, technical responses, and report composition flow.

### Modified Capabilities
- `pericia-points`: Extend the existing pericia-point capability so individual point execution can participate in a case-driven workflow and feed report-oriented responses.

## Impact

- Affects the future Django domain model for cases, evidence, requested points, and report generation.
- Shapes future admin/UI workflows for creating a new pericia, attaching evidence, selecting analysis strategies, and reviewing responses.
- Builds directly on the existing `pericia-points` capability and its execution/finding model.
- Introduces a report-oriented contract that future Celery jobs, extractors, storage layout, and template generation will need to follow.
