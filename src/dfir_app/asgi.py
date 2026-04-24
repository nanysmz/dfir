"""ASGI config for the DFIR application."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dfir_app.settings")

application = get_asgi_application()
