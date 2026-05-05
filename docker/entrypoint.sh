#!/bin/sh
set -eu

if [ -d /app/src ]; then
    export PYTHONPATH="/app/src:/app${PYTHONPATH:+:$PYTHONPATH}"
fi

if [ "${1:-}" = "web" ]; then
    python manage.py migrate --noinput
    python manage.py ensure_admin
    exec python manage.py runserver 0.0.0.0:8000
fi

exec "$@"
