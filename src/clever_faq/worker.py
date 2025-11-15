from dishka import AsyncContainer, make_async_container
from dishka.integrations.taskiq import setup_dishka
from sqlalchemy.orm import clear_mappers
from taskiq import AsyncBroker, TaskiqEvents, TaskiqState

from clever_faq.setup.bootstrap import (
    setup_map_tables,
    setup_task_manager,
    setup_task_manager_middlewares,
    setup_task_manager_tasks,
)
from clever_faq.setup.config.asgi import ASGIConfig
from clever_faq.setup.config.cache import RedisConfig
from clever_faq.setup.config.database import PostgresConfig, SQLAlchemyConfig
from clever_faq.setup.config.s3 import S3Config
from clever_faq.setup.config.settings import AppConfig
from clever_faq.setup.ioc import setup_providers


async def startup(state: TaskiqState) -> None:  # noqa: ARG001
    setup_map_tables()


async def shutdown(state: TaskiqState) -> None:  # noqa: ARG001
    clear_mappers()


def create_worker_taskiq_app() -> AsyncBroker:
    configs: AppConfig = AppConfig()
    task_manager: AsyncBroker = setup_task_manager(
        taskiq_config=configs.worker, rabbitmq_config=configs.rabbitmq, redis_config=configs.redis
    )
    task_manager_with_middlewares: AsyncBroker = setup_task_manager_middlewares(
        broker=task_manager,
        taskiq_config=configs.worker,
    )
    setup_task_manager_tasks(broker=task_manager_with_middlewares)

    task_manager.on_event(TaskiqEvents.WORKER_STARTUP)(startup)
    task_manager.on_event(TaskiqEvents.CLIENT_SHUTDOWN)(shutdown)

    context = {
        ASGIConfig: configs.asgi,
        RedisConfig: configs.redis,
        SQLAlchemyConfig: configs.alchemy,
        PostgresConfig: configs.postgres,
        S3Config: configs.s3,
        AsyncBroker: task_manager,
    }

    container: AsyncContainer = make_async_container(*setup_providers(), context=context)

    setup_dishka(container, broker=task_manager)

    return task_manager
