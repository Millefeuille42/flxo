# flxo - Backend

Backend service for flxo.
The backend is built with FastAPI, SQLModel, Authlib, and Alembic.

---

## Setup
The package management is done using UV.

### Install dependencies
```bash
uv venv
uv sync
source .venv/bin/activate  # Optional
```

### Set up and migrate the database
```bash
uv run alembic upgrade head
```

## Configuration

Configuration is read in order from env, TOML file and YAML file.
TOML and YAML file paths are specified via the environment:

```bash
TOML_FILE_PATH=/path/to/toml/file  # Defaults to "./config.toml"
YAML_FILE_PATH=/path/to/yaml/file  # Defaults to "./config.yaml"
```

Besides those two, env variables are prefixed by `FLXO__` 
and nested fields are separated by `__` (see example below for reference)

### Configuration example
The values provided in the example are the default ones
```toml
[app]
secret_key = "unsecure-key"  # would be FLXO__APP__SECRET_KEY as env
bind = "0.0.0.0"  # FLXO__APP__BIND
port = "8080"  # FLXO__APP_PORT
access_url = "http://localhost:8000" 
allowed_origins = "http://localhost:5173"
algorithm = "HS256"
access_token_expire_minutes = "30"

[db]
driver = "postgresql"  # postgresql or sqlite
host = "localhost"  # host for postgresql; acts as the path for sqlite
database = "flxo"
user = "flxo"
password = "flxo"
port = 5432

[oauth]
client_id = ""
client_secret = ""
scope = "openid email profile"

# Not default values here; using example values for clarity
authorize_url = "https://auth.example.com/application/o/authorize/"
access_token_url = "https://auth.example.com/application/o/token/"
metadata_url = "https://auth.example.com/application/o/dev/.well-known/openid-configuration"

```

## Running
To run from the backend folder.

### Dev
```bash
uv run fastpi dev flxo
```

### Production
```bash
uv run uvicorn flxo:app --host 0.0.0.0 --port 80
```


## Formatting and static analysis
```bash
uv run ruff check flxo
uv run ruff format flxo
uv run mypy flxo
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