FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.10 /uv /uvx /bin/

ARG DATABASE_DRIVER=sqlite

RUN apt-get update --yes --quiet && \
    apt-get install --yes --quiet --no-install-recommends build-essential && \
    if [ "$DATABASE_DRIVER" = "postgresql" ]; then \
        apt-get install --yes --quiet --no-install-recommends python3-psycopg2 libpq-dev; \
    fi && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=pyproject.toml \
    if [ "$DATABASE_DRIVER" = "postgresql" ]; then \
        uv sync --locked --no-install-project --no-editable --extra postgresql; \
    else \
        uv sync --locked --no-install-project --no-editable; \
    fi

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$DATABASE_DRIVER" = "postgresql" ]; then \
        uv sync --locked --no-editable --extra postgresql; \
    else \
        uv sync --locked --no-editable; \
    fi

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN useradd app
USER app
WORKDIR /app

COPY --chown=app:app . /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
RUN mkdir -p /app/data && chmod 700 /app/data

ENTRYPOINT ["/app/entrypoint.sh"]
