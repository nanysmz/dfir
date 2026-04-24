# DFIR Runtime

This project runs locally with Docker Compose. The launcher CLI asks where the
evidence input and output directories are mounted on the host, exports runtime
variables for that Docker Compose invocation, builds the shared application
image only when it is missing or explicitly requested, and starts Docker Compose.
Normal operation does not require a host Python virtual environment.
The runtime contains:

- Django web service
- Celery worker service
- Redis broker
- Postgres database

## Prerequisites

- macOS or Windows: install Docker Desktop and make sure any external evidence path is shared with Docker Desktop.
- Linux: install Docker Engine with the Docker Compose plugin.
- No host Python or virtual environment is required for normal use.

## Evidence Mounts

The host paths can change each time the runtime starts. Inside the containers they are always fixed:

- `/evidence/input`: selected evidence input directory, mounted read-only
- `/evidence/output`: selected output directory, mounted writable

The CLI expects the operating system to have already mounted USB drives, external disks, or internal disks as file-system paths. This skeleton does not pass raw block devices into containers and does not mount devices at the OS level.

## Admin User

When the `web` service starts, it runs Django migrations and then ensures an
admin superuser exists from the container entrypoint
(`docker/entrypoint.sh`). The command is idempotent: if the username already
exists, it updates email, staff/superuser flags, and password from the current
environment.

Defaults:

- `DJANGO_SUPERUSER_USERNAME=admin`
- `DJANGO_SUPERUSER_EMAIL=admin@example.local`
- `DJANGO_SUPERUSER_PASSWORD=admin`

Override them before running the launcher:

```bash
export DJANGO_SUPERUSER_USERNAME=perito
export DJANGO_SUPERUSER_EMAIL=perito@example.local
export DJANGO_SUPERUSER_PASSWORD='change-this-password'
bin/dfirctl
```

Windows PowerShell:

```powershell
$env:DJANGO_SUPERUSER_USERNAME = "perito"
$env:DJANGO_SUPERUSER_EMAIL = "perito@example.local"
$env:DJANGO_SUPERUSER_PASSWORD = "change-this-password"
.\bin\dfirctl.ps1
```

The launcher does not write an `.env` file. Change the environment variables
and rerun the launcher to rotate the admin password.

## Quick Start

Create local evidence directories for a first smoke run:

```bash
mkdir -p .local/evidence/input .local/evidence/output
```

Start interactively on macOS/Linux:

```bash
bin/dfirctl
```

Start interactively on Windows PowerShell:

```powershell
.\bin\dfirctl.ps1
```

The CLI prompts for:

- Evidence input directory mounted read-only at `/evidence/input`
- Evidence output directory mounted writable at `/evidence/output`

When possible, the launcher opens a visual folder picker:

- macOS: Finder folder chooser
- Windows: PowerShell folder browser dialog
- Linux: `zenity`, `qarma`, or `kdialog` if installed

If no visual picker is available, it falls back to a text prompt.

You can also pass paths without prompts on macOS/Linux:

```bash
bin/dfirctl \
  --input "$PWD/.local/evidence/input" \
  --output "$PWD/.local/evidence/output"
```

Or on Windows PowerShell:

```powershell
.\bin\dfirctl.ps1 `
  -InputPath .\.local\evidence\input `
  -OutputPath .\.local\evidence\output
```

Open `http://localhost:8000/health/` and expect `{"status": "ok"}`.

Stop the stack without deleting database data:

```bash
bin/dfirctl --down
```

Windows PowerShell:

```powershell
.\bin\dfirctl.ps1 -Down
```

## External Device Examples

macOS:

```bash
bin/dfirctl \
  --input /Volumes/EVIDENCE/source \
  --output /Volumes/EVIDENCE/output
```

Windows PowerShell:

```powershell
.\bin\dfirctl.ps1 `
  -InputPath E:\evidence\source `
  -OutputPath E:\evidence\output
```

Linux:

```bash
bin/dfirctl \
  --input /mnt/evidence/source \
  --output /mnt/evidence/output
```

The launcher validates that both host directories exist before starting Docker
Compose.

Changing evidence directories does not require rebuilding the image. The
launcher only rebuilds automatically when `dfir-app:local` does not exist. Use
`--build` on macOS/Linux or `-Build` on Windows when code or dependency changes
should be baked into the image.

## Dockerized Checks

Run tests:

```bash
docker compose build web
docker compose run --rm test
```

Run style checks:

```bash
docker compose build web
docker compose run --rm lint
```

## Smoke Check

Create local sample directories, start the stack, inspect service status, and
ping Celery:

```bash
mkdir -p .local/evidence/input .local/evidence/output
bin/dfirctl \
  --input "$PWD/.local/evidence/input" \
  --output "$PWD/.local/evidence/output"
docker compose ps
docker compose exec worker celery -A dfir_app inspect ping
```

## Limitations

- Pericia points are modeled and executable for normalized text and placeholder
  image-label analysis, but PDF/ofimática extractors and real CV/OCR engines are
  not implemented yet. See [docs/pericia-points.md](pericia-points.md).
- No chain-of-custody, hashing, or report generation is implemented yet.
- No raw block-device pass-through is configured.
- No automatic OS-level device mounting is performed.
