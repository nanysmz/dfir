from __future__ import annotations

import importlib
from pathlib import Path


def test_settings_read_runtime_environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "casework")
    monkeypatch.setenv("POSTGRES_USER", "analyst")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_HOST", "db-host")
    monkeypatch.setenv("POSTGRES_PORT", "5544")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://broker:6379/3")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://broker:6379/4")
    monkeypatch.setenv("EVIDENCE_INPUT_PATH", "/custom/input")
    monkeypatch.setenv("EVIDENCE_OUTPUT_PATH", "/custom/output")

    import dfir_app.settings as settings

    settings = importlib.reload(settings)

    assert settings.DATABASES["default"]["NAME"] == "casework"
    assert settings.DATABASES["default"]["USER"] == "analyst"
    assert settings.DATABASES["default"]["PASSWORD"] == "secret"
    assert settings.DATABASES["default"]["HOST"] == "db-host"
    assert settings.DATABASES["default"]["PORT"] == "5544"
    assert settings.CELERY_BROKER_URL == "redis://broker:6379/3"
    assert settings.CELERY_RESULT_BACKEND == "redis://broker:6379/4"
    assert str(settings.EVIDENCE_INPUT_PATH) == "/custom/input"
    assert str(settings.EVIDENCE_OUTPUT_PATH) == "/custom/output"


def test_settings_resolve_project_templates_dir():
    import dfir_app.settings as settings

    settings = importlib.reload(settings)
    template_dir = Path(settings.TEMPLATES[0]["DIRS"][0])

    assert template_dir.name == "templates"
    assert (template_dir / "admin" / "index.html").exists()
