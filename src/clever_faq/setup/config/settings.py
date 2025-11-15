import os

# from dotenv import load_dotenv
from pydantic import BaseModel, Field

from clever_faq.setup.config.asgi import ASGIConfig
from clever_faq.setup.config.cache import RedisConfig
from clever_faq.setup.config.chroma import ChromaDBConfig
from clever_faq.setup.config.database import PostgresConfig, SQLAlchemyConfig
from clever_faq.setup.config.openai import OpenAIEmbeddingsSettings, OpenAISettings
from clever_faq.setup.config.rabbit import RabbitConfig
from clever_faq.setup.config.s3 import S3Config
from clever_faq.setup.config.worker import TaskIQWorkerConfig


class AppConfig(BaseModel):
   #  load_dotenv(r"D:\Progrramming\PycharmProjects\clever-faq\.env")

    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(**os.environ),
        description="Postgres settings",
    )
    chroma: ChromaDBConfig = Field(
        default_factory=lambda: ChromaDBConfig(**os.environ),
        description="Chroma settings",
    )
    alchemy: SQLAlchemyConfig = Field(
        default_factory=lambda: SQLAlchemyConfig(**os.environ),
        description="SQLAlchemy settings",
    )
    rabbitmq: RabbitConfig = Field(
        default_factory=lambda: RabbitConfig(**os.environ),
        description="RabbitMQ settings",
    )
    redis: RedisConfig = Field(
        default_factory=lambda: RedisConfig(**os.environ),
        description="Redis settings",
    )
    worker: TaskIQWorkerConfig = Field(
        default_factory=lambda: TaskIQWorkerConfig(**os.environ),
        description="Worker settings",
    )
    asgi: ASGIConfig = Field(
        default_factory=lambda: ASGIConfig(**os.environ),
        description="ASGI settings",
    )
    s3: S3Config = Field(
        default_factory=lambda: S3Config(**os.environ),
        description="S3 settings",
    )
    openai: OpenAISettings = Field(
        default_factory=lambda: OpenAISettings(**os.environ),
    )
