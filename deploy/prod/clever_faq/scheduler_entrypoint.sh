#!/bin/sh
set -e

echo 'Running taskiq scheduler...'
python -m taskiq scheduler -fsd clever_faq.scheduler:create_scheduler_taskiq_app -tp clever_faq.infrastructure.scheduler.tasks
