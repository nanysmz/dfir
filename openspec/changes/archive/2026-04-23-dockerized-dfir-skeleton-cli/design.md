## Context

The project is starting with the runtime foundation for a digital forensics and incident response web application. The desired system will eventually ingest evidence files, execute pericia-specific analysis strategies asynchronously, persist case and processing metadata, expose visual results, and generate technical reports. This change focuses on the first layer: a reproducible local stack and a launcher CLI that asks for host evidence paths and starts Docker Compose with those paths.

The runtime must work on macOS, Windows, and Linux through Docker. Evidence sources and outputs can be external USB storage, large external disks, internal disks, or host directories that change between executions. The application must not assume fixed host paths.

As of April 21, 2026, the implementation should target current stable runtime families: Python 3.14.x, Django 6.0.x, Celery 5.6.x, PostgreSQL 18.x, and Redis 8.x, with exact patch versions pinned during implementation and kept easy to update.

## Goals / Non-Goals

**Goals:**

- Provide a Django web service container, Celery worker container, Redis service, and Postgres service.
- Provide Docker Compose configuration that can be launched consistently from macOS, Windows, and Linux.
- Provide a launcher CLI that prompts for evidence input/output host paths, validates them, writes runtime configuration, and starts Docker Compose.
- Establish stable in-container mount points for evidence input and generated output.
- Keep configuration explicit through environment files and documented defaults.
- Leave space for future pericia analysis modules, task queues, and report generation.

**Non-Goals:**

- Implement file analysis strategies, pericia workflows, report generation, or rich web UI in this change.
- Implement production deployment, authentication, multi-user authorization, or encrypted evidence vaulting.
- Automate operating-system-level disk mounting. The user or OS must make devices visible as host paths before the CLI uses them.
- Guarantee raw block-device access from containers. This initial skeleton operates on mounted file-system paths.

## Decisions

1. Use Docker Compose as the primary local orchestration layer.

   Docker Compose is widely available with Docker Desktop on macOS and Windows and with Docker Engine on Linux. It gives enough structure for Django, Celery, Redis, and Postgres without introducing Kubernetes or host-specific service managers. Alternatives considered: shell scripts only, which would duplicate orchestration logic; Kubernetes, which is too heavy for the initial local DFIR workflow.

2. Build Django and Celery from the same application image.

   A single Python application image avoids dependency drift between web and worker containers. The web service runs the Django server command, while the worker service runs the Celery worker command. Alternatives considered: separate Dockerfiles, which are useful later only if the worker gets significantly different system dependencies.

3. Use named volumes for database state and bind mounts for evidence paths.

   Postgres data belongs in a named Docker volume so it survives container restarts. Evidence input and output must remain host-visible and selectable per run, so they use bind mounts supplied by the CLI. Alternatives considered: copying evidence into Docker volumes, which hides source/output paths from investigators and is poor for large disks.

4. Standardize in-container evidence paths.

   The CLI maps host input to `/evidence/input` and host output to `/evidence/output`. Application code can depend on these stable paths while the host paths vary by run. Input mounts should default to read-only; output mounts must be writable. Alternatives considered: exposing arbitrary host paths to the app, which makes code and documentation harder to keep portable.

5. Implement the operator launcher as small host scripts that require only Docker.

   Bash and PowerShell launchers avoid a host Python virtualenv while still supporting macOS/Linux and Windows. They prompt for evidence paths, prefer native folder-picker dialogs when available, export runtime variables for the current Compose invocation, reuse the existing shared image when present, and start Docker Compose. They build only when the image is missing or when the operator passes an explicit build flag. Alternatives considered: a host Python CLI, which conflicts with the no-venv workflow; a Dockerized CLI that starts Docker, which would require Docker socket mounting and more platform-specific handling; an env-file based workflow, which the operator does not want; always rebuilding, which is wasteful when only evidence mounts change; a GUI launcher, which is premature.

6. Pass runtime configuration through process environment variables before invoking Compose.

   The launcher should export normalized host paths and service settings in its own process before invoking Docker Compose. This keeps Compose declarative without writing `.env` files to disk. Alternatives considered: a local ignored env file, which is convenient but was explicitly ruled out; passing many `-e` flags directly, which is harder to inspect and troubleshoot.

7. Keep device access conservative.

   The first implementation requires already-mounted file-system paths and avoids privileged containers. Linux-only raw device pass-through can be considered later if a future capability requires disk imaging or block-level parsing. This preserves cross-platform behavior and reduces accidental evidence modification risk.

## Risks / Trade-offs

- Host path syntax differs across operating systems -> Provide Bash and PowerShell launchers that validate paths using the host operating system before Docker Compose receives them.
- Docker Desktop file sharing can block macOS/Windows external paths -> The CLI cannot configure Docker Desktop automatically, so errors must explain that the path must be shared with Docker.
- Large evidence trees can be slow through bind mounts on macOS/Windows -> The skeleton prioritizes correctness and portability; later analysis tasks can add staging, indexing, or platform-specific performance guidance.
- Evidence integrity could be harmed by accidental writes -> Input mounts default to read-only and application code uses a separate output mount.
- Latest stable versions can change -> Pin exact versions in dependency files during implementation, but keep them centralized and easy to update.
- Celery tasks may start before Django migrations are ready -> Compose health checks and startup commands should make readiness explicit.

## Migration Plan

This is an initial skeleton, so no data migration is required. Implementation should add the container, CLI, and configuration files in a way that existing repository content can coexist with the new runtime. Rollback is removing the new change files and generated application skeleton if implementation is not adopted.

## Open Questions

- Should the first Django project name be `dfir`, `dfir_app`, or another project-specific name?
- Should the CLI later package as PyInstaller binaries per OS, or remain Docker-only?
- Which evidence hashing and chain-of-custody requirements should be introduced in the next capability?
