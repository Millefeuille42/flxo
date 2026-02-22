# flxo - Backend

Backend service for flxo.
The backend is built with FastAPI, SQLModel, Authlib, and Alembic.

---

## Setup
The package management is done using UV.

### Install dependencies

**For SQLite (default):**
```bash
uv venv
uv sync
source .venv/bin/activate  # Optional
```

**For PostgreSQL:**
```bash
uv venv
uv sync --extra postgresql
source .venv/bin/activate  # Optional
```

### Configuration

Configuration is read in order of priority (highest to lowest):
1. **Environment variables** (prefixed with `FLXO__`)
2. **TOML file** (default: `config.toml`)
3. **YAML file** (default: `config.yaml`)
4. **Default values** in code

TOML and YAML file paths can be customized via environment variables:
```bash
TOML_FILE_PATH=/path/to/toml/file  # Defaults to "./config.toml"
YAML_FILE_PATH=/path/to/yaml/file  # Defaults to "./config.yaml"
```

Environment variables use the prefix `FLXO__` and nested fields are separated by `__`.

### Configuration Examples

**Example configuration files are provided:**
- `config.sqlite.example.toml` - SQLite configuration for development
- `config.postgresql.example.toml` - PostgreSQL configuration for production
- `.env.example` - Environment variables examples

Copy the appropriate example file to get started:
```bash
# For SQLite (recommended for development)
cp config.sqlite.example.toml config.toml

# For PostgreSQL (recommended for production)
cp config.postgresql.example.toml config.toml

# Or use environment variables
cp .env.example .env
```

### Database Configuration

**SQLite Configuration:**
```toml
[db]
driver = "sqlite"
host = "flxo.db"  # Relative path, absolute path, or ":memory:"
```

**PostgreSQL Configuration:**
```toml
[db]
driver = "postgresql"
host = "localhost"
database = "flxo"
user = "flxo"
password = "flxo"
port = 5432
```

**Using Environment Variables:**
```bash
# SQLite
export FLXO__DB__DRIVER=sqlite
export FLXO__DB__HOST=flxo.db

# PostgreSQL
export FLXO__DB__DRIVER=postgresql
export FLXO__DB__HOST=localhost
export FLXO__DB__DATABASE=flxo
export FLXO__DB__USER=flxo
export FLXO__DB__PASSWORD=flxo
export FLXO__DB__PORT=5432
```

## Set up and migrate the database
```bash
uv run alembic upgrade head
```

## Running

### Local Development
From the backend folder:

```bash
# Development mode with auto-reload
uv run fastapi dev flxo

# Production mode
uv run uvicorn flxo:app --host 0.0.0.0 --port 80
```

### Docker Deployment

**SQLite (default):**
```bash
# From project root
docker-compose up

# Access API at http://localhost:8080/docs
# Database is persisted in Docker volume 'flxo_sqlite_data'
```

**PostgreSQL:**
```bash
# Create .env file with PostgreSQL configuration
cp .env.docker.postgres.example .env

# Start with PostgreSQL profile
docker-compose --profile postgres up

# Access API at http://localhost:8080/docs
```

**Note:** The SQLite database is stored in a Docker named volume (`sqlite_data`) for proper permission handling. To backup or inspect the database:
```bash
# Backup SQLite database
docker-compose exec -T backend sqlite3 /app/data/flxo.db .dump > backup.sql

# Access the database directly
docker-compose exec backend sqlite3 /app/data/flxo.db
```


## Migrating Between Databases

### From PostgreSQL to SQLite

1. Export data from PostgreSQL (if needed):
   ```bash
   pg_dump -h localhost -U flxo flxo > backup.sql
   ```

2. Update configuration to use SQLite:
   ```bash
   export FLXO__DB__DRIVER=sqlite
   export FLXO__DB__HOST=flxo.db
   ```

3. Run migrations:
   ```bash
   uv run alembic upgrade head
   ```

4. Re-import data manually if needed (SQL syntax may differ)

### From SQLite to PostgreSQL

1. Backup SQLite database:
   ```bash
   cp flxo.db flxo.db.backup
   ```

2. Install PostgreSQL dependencies:
   ```bash
   uv sync --extra postgresql
   ```

3. Update configuration to use PostgreSQL

4. Run migrations:
   ```bash
   uv run alembic upgrade head
   ```

5. Migrate data using a migration script or manual export/import

---

## Troubleshooting

### "PostgreSQL driver (psycopg2-binary) is not installed"

**Cause:** You configured PostgreSQL but didn't install the PostgreSQL dependencies.

**Solution:**
```bash
uv sync --extra postgresql
```

### "database is locked" (SQLite)

**Cause:** Multiple processes trying to write to SQLite simultaneously, or a process crashed while holding a lock.

**Solutions:**
- Use only one worker/process with SQLite: `uvicorn flxo:app --workers 1`
- For production with multiple workers, use PostgreSQL instead
- If persists, check for zombie processes: `fuser flxo.db` (Linux) or restart the application

### SQLite file not found

**Cause:** Incorrect path in configuration or insufficient permissions.

**Solutions:**
- Use absolute path: `FLXO__DB__HOST=/var/lib/flxo/flxo.db`
- Ensure directory exists: `mkdir -p /var/lib/flxo`
- Check file permissions: `chmod 644 /var/lib/flxo/flxo.db`

### Migrations fail

**Cause:** Database schema out of sync or migration conflict.

**Solutions:**
```bash
# Check current migration version
uv run alembic current

# Downgrade to a specific version if needed
uv run alembic downgrade <revision>

# Upgrade to latest
uv run alembic upgrade head
```

---

## Formatting and static analysis
```bash
uv run ruff check flxo
uv run ty check flxo
uv run ruff format flxo
```

## API Documentation
Once running:

Swagger UI: http://localhost:8000/docs

## Contributing

Use uv to manage environment and commands.
Ensure type checks and formatting pass before committing.
Follow routing/service layering conventions.

## License
Backend is licensed under the MIT License as the rest of the project. See [LICENSE](../LICENSE) for details.