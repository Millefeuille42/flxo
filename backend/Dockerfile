FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    python3-psycopg2 \
    libpq-dev \
    libmariadb-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN useradd app
USER app
WORKDIR /app

COPY --chown=app:app . /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv

ENTRYPOINT ["/app/entrypoint.sh"]
