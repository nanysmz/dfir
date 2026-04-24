# DFIR

Dockerized skeleton for a digital forensics evidence-analysis application.

The initial runtime includes Django, Celery, Redis, Postgres, and a
cross-platform launcher CLI that asks for evidence input/output paths and starts
Docker Compose with those mounts.

See [docs/runtime.md](docs/runtime.md) for prerequisites, examples, fixed
container paths, smoke checks, and current limitations. No local Python virtual
environment is required for normal use.

The initial pericia domain model is documented in
[docs/pericia-points.md](docs/pericia-points.md).

macOS/Linux:

```bash
bin/dfirctl
```

Windows PowerShell:

```powershell
.\bin\dfirctl.ps1
```
