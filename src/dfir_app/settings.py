"""Django settings for the local Dockerized DFIR runtime."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_base_dir() -> Path:
    candidates = [
        Path.cwd(),
        Path("/app"),
        Path(__file__).resolve().parents[2],
    ]
    for candidate in candidates:
        if (candidate / "manage.py").exists():
            return candidate
    for candidate in candidates:
        if (candidate / "templates").exists() and (candidate / "src").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


BASE_DIR = resolve_base_dir()


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


SECRET_KEY = env("DJANGO_SECRET_KEY", "local-dev-insecure-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [
    host.strip()
    for host in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dfir_cases",
    "dfir_evidence",
    "dfir_analysis",
    "dfir_reports",
    "dfir_core",
    "dfir_pericia",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dfir_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dfir_app.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "dfir"),
        "USER": env("POSTGRES_USER", "dfir"),
        "PASSWORD": env("POSTGRES_PASSWORD", "dfir"),
        "HOST": env("POSTGRES_HOST", "postgres"),
        "PORT": env("POSTGRES_PORT", "5432"),
    }
}

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EVIDENCE_INPUT_PATH = Path(env("EVIDENCE_INPUT_PATH", "/evidence/input"))
EVIDENCE_OUTPUT_PATH = Path(env("EVIDENCE_OUTPUT_PATH", "/evidence/output"))

CELERY_BROKER_URL = env("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", False)
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(env("DJANGO_DATA_UPLOAD_MAX_NUMBER_FIELDS", "20000"))

UNFOLD = {
    "SITE_TITLE": "DFIR",
    "SITE_HEADER": "DFIR",
    "SITE_SUBHEADER": "Backoffice pericial",
    "SITE_SYMBOL": "search_insights",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "DASHBOARD_CALLBACK": "dfir_core.admin.dashboard_callback",
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Flujo pericial",
                "separator": True,
                "items": [
                    {"title": "Inicio", "icon": "space_dashboard", "link": "/admin/"},
                    {
                        "title": "Casos periciales",
                        "icon": "folder_managed",
                        "link": "/admin/dfir_cases/periciacaseproxy/",
                    },
                    {
                        "title": "Evidencia",
                        "icon": "inventory_2",
                        "link": "/admin/dfir_evidence/evidenceitemproxy/",
                    },
                    {
                        "title": "Analisis",
                        "icon": "manage_search",
                        "link": "/admin/dfir_analysis/analysisplanproxy/",
                    },
                    {
                        "title": "Informe",
                        "icon": "description",
                        "link": "/admin/dfir_reports/reportsectionproxy/",
                    },
                ],
            },
            {
                "title": "Administracion del sistema",
                "separator": True,
                "items": [
                    {"title": "Usuarios", "icon": "people", "link": "/admin/auth/user/"},
                    {"title": "Grupos", "icon": "group_work", "link": "/admin/auth/group/"},
                ],
            },
        ]
    },
}
