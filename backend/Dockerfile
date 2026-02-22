FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Build argument to control database driver installation
ARG DATABASE_DRIVER=sqlite

# Install build dependencies conditionally
RUN apt-get update --yes --quiet && \
    apt-get install --yes --quiet --no-install-recommends build-essential && \
    if [ "$DATABASE_DRIVER" = "postgresql" ]; then \
        apt-get install --yes --quiet --no-install-recommends python3-psycopg2 libpq-dev; \
    fi && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY uv.lock pyproject.toml ./

# Install dependencies based on database driver
RUN if [ "$DATABASE_DRIVER" = "postgresql" ]; then \
        uv sync --locked --no-install-project --no-editable --extra postgresql; \
    else \
        uv sync --locked --no-install-project --no-editable; \
    fi

# Copy application code
COPY . /app

# Install the project
RUN if [ "$DATABASE_DRIVER" = "postgresql" ]; then \
        uv sync --locked --no-editable --extra postgresql; \
    else \
        uv sync --locked --no-editable; \
    fi

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN useradd app

WORKDIR /app

# Create data directory for SQLite with proper permissions
RUN mkdir -p /app/data && chown -R app:app /app/data

USER app

COPY --chown=app:app . /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv

ENTRYPOINT ["/app/entrypoint.sh"]
