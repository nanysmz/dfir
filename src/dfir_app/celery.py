"""Celery application for asynchronous DFIR work."""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dfir_app.settings")

app = Celery("dfir")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(name="dfir.health_check")
def health_check() -> str:
    return "ok"
