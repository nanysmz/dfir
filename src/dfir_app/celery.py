"""Celery application for asynchronous DFIR work."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from celery import Celery

src_path = Path(__file__).resolve().parents[2] / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dfir_app.settings")

app = Celery("dfir")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="dfir.health_check")
def health_check() -> str:
    return "ok"
