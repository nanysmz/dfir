FROM python:3.14.4-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
ARG INSTALL_DEV=false

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY manage.py ./
COPY docker ./docker

RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir ".[dev]"; \
    else \
        pip install --no-cache-dir .; \
    fi

RUN chmod +x docker/entrypoint.sh \
    && mkdir -p /evidence/input /evidence/output

EXPOSE 8000

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["web"]
