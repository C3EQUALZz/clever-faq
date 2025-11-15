#!/bin/sh
set -e

echo 'Running taskiq scheduler...'
taskiq scheduler -fsd clever_faq.scheduler:create_scheduler_taskiq_app -tp clever_faq.infrastructure.scheduler.tasks
