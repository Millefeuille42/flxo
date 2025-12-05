#! /bin/bash

/app/.venv/bin/alembic upgrade head
/app/.venv/bin/uvicorn flxo:app --host 0.0.0.0 --port 80 $@
