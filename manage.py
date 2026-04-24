#!/usr/bin/env python
"""Django administrative entry point."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    src_path = Path(__file__).resolve().parent / "src"
    sys.path.insert(0, str(src_path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dfir_app.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
