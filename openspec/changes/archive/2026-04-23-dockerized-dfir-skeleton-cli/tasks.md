## 1. Project Skeleton

- [x] 1.1 Inspect the repository layout and choose the Django project/package location without overwriting existing user work
- [x] 1.2 Add Python project metadata and pin stable runtime dependencies for Django, Celery, Redis client, Postgres driver, CLI tooling, and test tooling
- [x] 1.3 Create the Django project skeleton with settings that read database, Redis, evidence input, and evidence output configuration from environment variables
- [x] 1.4 Add Celery application initialization and a minimal health-check task that can be imported by the worker
- [x] 1.5 Add `.gitignore` entries for local runtime env files, Python caches, virtual environments, and generated local artifacts

## 2. Docker Runtime

- [x] 2.1 Add an application Dockerfile based on the pinned stable Python image and install project dependencies reproducibly
- [x] 2.2 Add Docker Compose services for web, worker, Redis, and Postgres using the shared application image for web and worker
- [x] 2.3 Configure Postgres with a named Docker volume and health check
- [x] 2.4 Configure Redis with a stable image tag and health check
- [x] 2.5 Configure web and worker services with `/evidence/input` and `/evidence/output` bind mounts driven by runtime env variables
- [x] 2.6 Ensure the input evidence mount is read-only and the output evidence mount is writable

## 3. CLI Orchestration

- [x] 3.1 Create cross-platform launcher CLIs that prompt for paths, write runtime configuration, and start Docker Compose
- [x] 3.2 Implement path normalization and existence validation for evidence input and output host paths
- [x] 3.3 Implement runtime environment export with absolute evidence paths and service configuration consumed by Docker Compose
- [x] 3.4 Add Docker Compose utility services for running tests and linting without a host virtualenv
- [x] 3.5 Document Docker Compose commands for stopping services without deleting volumes by default
- [x] 3.6 Document Docker Compose status checks and surface useful CLI errors for invalid or inaccessible paths

## 4. Verification

- [x] 4.1 Add unit tests for CLI path validation and runtime env file generation
- [x] 4.2 Add a lightweight Django configuration test that verifies database, Redis, and evidence paths are read from environment variables
- [x] 4.3 Add a smoke-test command or documented check that builds the shared image and starts web, worker, Redis, and Postgres through the CLI
- [x] 4.4 Verify the worker can import the Celery app and connect to Redis within the Compose network
- [x] 4.5 Verify missing evidence input or output paths fail before Docker Compose is invoked

## 5. Operator Documentation

- [x] 5.1 Document prerequisites for Docker Desktop on macOS/Windows and Docker Engine on Linux
- [x] 5.2 Document how to run the CLI with evidence input and output paths for macOS, Windows, and Linux examples
- [x] 5.3 Document the fixed in-container evidence paths `/evidence/input` and `/evidence/output`
- [x] 5.4 Document current non-goals and limitations, including no raw block-device pass-through and no automatic OS-level device mounting
