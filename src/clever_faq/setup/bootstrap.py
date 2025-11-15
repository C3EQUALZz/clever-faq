import logging
from functools import lru_cache
from types import TracebackType
from typing import Any, Final

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from taskiq import AsyncBroker, ScheduleSource, SmartRetryMiddleware, TaskiqScheduler, async_shared_broker
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import ListRedisScheduleSource, RedisAsyncResultBackend

from clever_faq.infrastructure.persistence.models.dialog import map_dialog_table
from clever_faq.infrastructure.scheduler.tasks.document_tasks import setup_documents_task
from clever_faq.presentation.http.v1.common.exception_handler import ExceptionHandler
from clever_faq.presentation.http.v1.middlewares.client_cache import ClientCacheMiddleware
from clever_faq.presentation.http.v1.middlewares.logs import LoggingMiddleware
from clever_faq.setup.config.asgi import ASGIConfig
from clever_faq.setup.config.cache import RedisConfig
from clever_faq.setup.config.rabbit import RabbitConfig
from clever_faq.setup.config.settings import AppConfig
from clever_faq.setup.config.worker import TaskIQWorkerConfig

logger: Final[logging.Logger] = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def setup_configs() -> AppConfig:
    return AppConfig()


def setup_map_tables() -> None:
    """
    Ensures imperative SQLAlchemy mappings are initialized at application startup.

    ### Purpose:
    In Clean Architecture, domain entities remain agnostic of database
    mappings. To integrate with SQLAlchemy, mappings must be explicitly
    triggered to link ORM attributes to domain classes. Without this setup,
    attempts to interact with unmapped entities in database operations
    will lead to runtime errors.

    ### Solution:
    This function provides a single entry point to initialize the mapping
    of domain entities to database tables. By calling the `setup_map_tables` function,
    ORM attributes are linked to domain classes without altering domain code
    or introducing infrastructure concerns.

    ### Usage:
    Call the `setup_map_tables` function in the application factory to initialize
    mappings at startup. Additionally, it is necessary to call this function
    in `env.py` for Alembic migrations to ensure all models are available
    during database migrations.
    """

    map_dialog_table()


def setup_http_middlewares(app: FastAPI, /, api_config: ASGIConfig) -> None:
    """
    Registers all middlewares for FastAPI application.

    Args:
        app: FastAPI application
        api_config: ASGIConfig
    Returns:
        None
    """
    app.add_middleware(
        CORSMiddleware,  # type: ignore[arg-type, unused-ignore]
        allow_origins=[
            f"http://localhost:{api_config.port}",
            f"https://{api_config.host}:{api_config.port}",
            f"http://127.0.0.1:{api_config.port}",
            "http://127.0.0.1",
        ],
        allow_credentials=api_config.allow_credentials,
        allow_methods=api_config.allow_methods,
        allow_headers=api_config.allow_headers,
    )
    app.add_middleware(ClientCacheMiddleware, max_age=60)  # type: ignore[arg-type, unused-ignore]
    app.add_middleware(LoggingMiddleware)  # type: ignore[arg-type, unused-ignore]


def setup_task_manager(
    taskiq_config: TaskIQWorkerConfig, rabbitmq_config: RabbitConfig, redis_config: RedisConfig
) -> AsyncBroker:
    logger.debug("Creating taskiq broker for task management....")
    broker: AsyncBroker = AioPikaBroker(
        url=rabbitmq_config.uri,
        declare_exchange=taskiq_config.declare_exchange,
        declare_queues_kwargs={"durable": taskiq_config.durable_queue},
        declare_exchange_kwargs={"durable": taskiq_config.durable_exchange},
    ).with_result_backend(
        RedisAsyncResultBackend(
            redis_url=redis_config.worker_uri,
            result_ex_time=1000,
        )
    )
    logger.debug("Set async shared broker")
    async_shared_broker.default_broker(broker)

    logger.debug("Returning taskiq broker")
    return broker


def setup_task_manager_middlewares(broker: AsyncBroker, taskiq_config: TaskIQWorkerConfig) -> AsyncBroker:
    logger.debug("Start setup broker middlewares")
    return broker.with_middlewares(
        SmartRetryMiddleware(
            default_retry_count=taskiq_config.default_retry_count,
            default_delay=taskiq_config.default_delay,
            use_jitter=taskiq_config.use_jitter,
            use_delay_exponent=taskiq_config.use_delay_exponent,
            max_delay_exponent=taskiq_config.max_delay_component,
        ),
    )


def setup_task_manager_tasks(broker: AsyncBroker) -> None:
    setup_documents_task(broker)


def setup_schedule_source(redis_config: RedisConfig) -> ScheduleSource:
    return ListRedisScheduleSource(url=redis_config.schedule_source_uri)


def setup_scheduler(broker: AsyncBroker, schedule_source: ScheduleSource) -> TaskiqScheduler:
    logger.debug("Creating taskiq scheduler for task management...")

    return TaskiqScheduler(
        broker=broker,
        sources=[
            LabelScheduleSource(broker),
            schedule_source,
        ],
    )


def setup_exc_handlers(app: FastAPI, /) -> None:
    """
    Registers exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance to configure
    """
    exception_handler: ExceptionHandler = ExceptionHandler(app)
    exception_handler.setup_handlers()


def global_exception_handler_with_traceback(
    exc_type: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
) -> Any:  # noqa: ANN401
    root_logger: logging.Logger = logging.getLogger()
    root_logger.exception("Error", exc_info=(exc_type, value, traceback))
