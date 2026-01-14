#! /bin/bash


/app/.venv/bin/alembic upgrade head

if [ "$FLXO__REVERSE_PROXY" = "true" ]; then
  echo "Starting with reverse proxy settings"
  /app/.venv/bin/uvicorn flxo:app --proxy-headers --forwarded-allow-ips "*" --host 0.0.0.0 --port 80 $@
else
  echo "Starting without reverse proxy settings"
  /app/.venv/bin/uvicorn flxo:app --host 0.0.0.0 --port 80 $@
fi

