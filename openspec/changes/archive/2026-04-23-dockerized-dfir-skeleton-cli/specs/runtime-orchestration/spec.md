## ADDED Requirements

### Requirement: Dockerized service composition
The system SHALL define a Docker Compose runtime containing Django web, Celery worker, Redis, and Postgres services.

#### Scenario: Runtime starts all core services
- **WHEN** the operator starts the runtime through the supported CLI
- **THEN** Docker Compose starts the web, worker, Redis, and Postgres services with the configured environment

#### Scenario: Web and worker share application image
- **WHEN** the Docker runtime is built
- **THEN** the Django web service and Celery worker service use the same application image with different startup commands

### Requirement: Stable runtime versions
The system SHALL use pinned, stable dependency versions for Python, Django, Celery, Postgres, and Redis.

#### Scenario: Dependency versions are inspectable
- **WHEN** an operator or developer reviews the runtime configuration
- **THEN** the selected Python, Django, Celery, Postgres, and Redis versions are visible in dependency or container configuration files

### Requirement: Interactive launcher runtime orchestration
The system SHALL provide a launcher CLI that asks for evidence input and output host paths, prepares runtime configuration, and starts the Dockerized runtime on macOS, Windows, and Linux.

#### Scenario: Prompt for paths
- **WHEN** the operator runs the launcher without evidence path arguments
- **THEN** the launcher asks for evidence input and output host directories

#### Scenario: Visual folder selection
- **WHEN** the operating system supports a folder chooser and the operator runs the launcher without evidence path arguments
- **THEN** the launcher offers visual folder selection for evidence input and output before falling back to text prompts

#### Scenario: Start runtime after configuration
- **WHEN** the operator provides valid evidence input and output host directories
- **THEN** the launcher writes runtime configuration and starts Docker Compose with those paths available to the services

#### Scenario: Show runtime status
- **WHEN** the operator runs the launcher status command
- **THEN** the launcher reports the current Docker Compose service state

### Requirement: Evidence input bind mount
The system SHALL mount the selected evidence input host path into application containers at `/evidence/input`.

#### Scenario: Input path exists
- **WHEN** the operator provides an existing evidence input path
- **THEN** the path is mounted at `/evidence/input` for application services

#### Scenario: Input path is missing
- **WHEN** the operator provides an evidence input path that does not exist
- **THEN** the launcher fails before starting Docker Compose and reports which path is invalid

#### Scenario: Input mount is read-only
- **WHEN** the runtime starts with an evidence input path
- **THEN** application containers receive the input mount as read-only by default

### Requirement: Evidence output bind mount
The system SHALL mount the selected evidence output host path into application containers at `/evidence/output`.

#### Scenario: Output path exists
- **WHEN** the operator provides an existing evidence output path
- **THEN** the path is mounted at `/evidence/output` for application services with write access

#### Scenario: Output path is missing
- **WHEN** the operator provides an evidence output path that does not exist
- **THEN** the launcher fails before starting Docker Compose and reports which path is invalid

### Requirement: Persistent database storage
The system SHALL persist Postgres data in a Docker-managed named volume.

#### Scenario: Runtime restarts
- **WHEN** the operator stops and starts the runtime without requesting volume deletion
- **THEN** Postgres data remains available after restart

### Requirement: Asynchronous task foundation
The system SHALL configure Django and Celery to use Redis as the broker for asynchronous work.

#### Scenario: Worker connects to broker
- **WHEN** the runtime starts
- **THEN** the Celery worker is configured to connect to the Redis service using runtime environment settings

#### Scenario: Django can enqueue future work
- **WHEN** Django code uses the configured Celery application
- **THEN** tasks are routed to Redis for worker execution

### Requirement: Local configuration isolation
The system SHALL keep generated runtime configuration out of version control.

#### Scenario: Launcher exports runtime configuration
- **WHEN** the launcher prepares a run with selected evidence paths
- **THEN** it exports runtime configuration for the Docker Compose invocation without requiring a committed env file
