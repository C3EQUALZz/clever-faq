#!/bin/sh
set -e

echo 'Running alembic migrations...'
python -m alembic upgrade head
echo 'Running taskiq tasks...'
python -m taskiq worker -fsd --ack-type when_saved clever_faq.worker:create_worker_taskiq_app -tp clever_faq.infrastructure.scheduler.tasks
