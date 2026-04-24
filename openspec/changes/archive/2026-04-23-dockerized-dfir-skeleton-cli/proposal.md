## Why

The DFIR application needs a reproducible local runtime before analysis features can be built safely. A Dockerized Django/Celery/Redis/Postgres skeleton plus a cross-platform CLI will make it possible to run the same evidence-processing environment on macOS, Windows, and Linux while selecting external evidence source and output locations per run.

## What Changes

- Add a Dockerized application skeleton for Django, Celery worker, Redis, and Postgres.
- Add a cross-platform launcher CLI that prompts for host evidence paths, prepares runtime configuration, and starts Docker Compose.
- Support per-run configuration for evidence input and output mounts, including large external USB drives, external disks, and internal disks.
- Establish environment configuration, volume conventions, and service boundaries for future digital-evidence analysis workflows.
- Define the first runtime contract for safely passing host evidence paths into containers without hard-coding machine-specific paths.

## Capabilities

### New Capabilities

- `runtime-orchestration`: Covers the Dockerized runtime, service composition, interactive launcher flow, and host evidence path mounting behavior.

### Modified Capabilities

- None.

## Impact

- Adds project structure for a Django web application, Celery worker, Redis broker, and Postgres database.
- Adds Dockerfile and Docker Compose assets for local development across supported operating systems.
- Adds launcher scripts for macOS/Linux and Windows that prepare selected evidence source/destination paths and start Docker Compose.
- Introduces configuration files for application settings, database connection, Celery broker/result backend, and bind-mounted evidence directories.
- Future analysis, pericia, and report-generation features will build on this runtime foundation.
