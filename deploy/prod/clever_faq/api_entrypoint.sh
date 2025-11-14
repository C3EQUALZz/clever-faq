#!/bin/sh
set -e

echo 'Running alembic migrations...'
python -m alembic upgrade head
echo 'Starting Uvicorn...'
python -Om src.clever_faq.web