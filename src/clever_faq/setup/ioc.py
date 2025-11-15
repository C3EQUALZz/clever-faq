from collections.abc import Iterable
from typing import Final

from dishka import Provider, Scope
from dishka.integrations.fastapi import FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession

from clever_faq.application.commands.document.create_document import CreateDocumentCommandHandler
from clever_faq.application.commands.document.retrieval_augmentation_for_document import (
    RetrievalAugmentationForDocumentCommandHandler,
)
from clever_faq.application.commands.questions.answer_the_question import AnswerTheQuestionCommandHandler
from clever_faq.application.common.ports.cache_store import CacheStore
from clever_faq.application.common.ports.dialog.dialog_command_gateway import DialogCommandGateway
from clever_faq.application.common.ports.document.document_command_gateway import DocumentCommandGateway
from clever_faq.application.common.ports.document.document_storage import DocumentStorage
from clever_faq.application.common.ports.question.question_answering_port import QuestionAnsweringPort
from clever_faq.application.common.ports.scheduler.task_scheduler import TaskScheduler
from clever_faq.application.common.ports.transaction_manager import TransactionManager
from clever_faq.domain.dialog.ports.dialog_id_generator import DialogIDGenerator
from clever_faq.domain.dialog.services.dialog_service import DialogService
from clever_faq.domain.document.ports.chunk_id_generator import ChunkIDGenerator
from clever_faq.domain.document.ports.document_id_generator import DocumentIDGenerator
from clever_faq.domain.document.ports.text_splitter import TextSplitter
from clever_faq.domain.document.services.document import DocumentService
from clever_faq.infrastructure.adapters.common.langchain_text_splitter import SemanticTextSplitter
from clever_faq.infrastructure.adapters.common.uuid4_chunk_id_generator import UUID4ChunkIDGenerator
from clever_faq.infrastructure.adapters.common.uuid4_dialog_id_generator import UUID4DialogIDGenerator
from clever_faq.infrastructure.adapters.common.uuid4_document_id_generator import UUID4DocumentIDGenerator
from clever_faq.infrastructure.adapters.file.provider import get_file_processor_factory
from clever_faq.infrastructure.adapters.question.langchain_question_answering_port import LangChainQuestionAnsweringPort
from clever_faq.infrastructure.adapters.question.provider import get_chat_model, get_embeddings
from clever_faq.infrastructure.cache.adapters.cached_question_answering_port import CachedQuestionAnsweringPort
from clever_faq.infrastructure.cache.provider import get_redis, get_redis_pool
from clever_faq.infrastructure.cache.redis_cache_store import RedisCacheStore
from clever_faq.infrastructure.persistence.adapters.aiobotocore_document_storage import AiobotocoreDocumentStorage
from clever_faq.infrastructure.persistence.adapters.alchemy_dialog_command_gateway import SqlAlchemyDialogCommandGateway
from clever_faq.infrastructure.persistence.adapters.alchemy_transaction_manager import SQLAlchemyTransactionManager
from clever_faq.infrastructure.persistence.adapters.langchain_document_command_gateway import (
    LangchainVectorStoreGateway,
)
from clever_faq.infrastructure.persistence.provider import (
    get_engine,
    get_s3_client,
    get_s3_session,
    get_session,
    get_sessionmaker,
    get_vector_store,
)
from clever_faq.infrastructure.scheduler.task_iq_task_scheduler import TaskIQTaskScheduler
from clever_faq.setup.config.asgi import ASGIConfig
from clever_faq.setup.config.cache import RedisConfig
from clever_faq.setup.config.chroma import ChromaDBConfig
from clever_faq.setup.config.database import PostgresConfig, SQLAlchemyConfig
from clever_faq.setup.config.openai import OpenAISettings


def configs_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.APP)
    provider.from_context(ASGIConfig)
    provider.from_context(ChromaDBConfig)
    provider.from_context(OpenAISettings)
    provider.from_context(SQLAlchemyConfig)
    provider.from_context(PostgresConfig)
    provider.from_context(RedisConfig)
    return provider


def db_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(get_vector_store)
    provider.provide(get_embeddings)
    provider.provide(get_chat_model)
    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_sessionmaker, scope=Scope.APP)
    provider.provide(get_session, provides=AsyncSession)
    provider.provide(get_s3_session)
    provider.provide(get_s3_client)
    return provider


def cache_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(get_redis_pool, scope=Scope.APP)
    provider.provide(get_redis)
    provider.provide(RedisCacheStore, provides=CacheStore)
    provider.decorate(CachedQuestionAnsweringPort, provides=QuestionAnsweringPort)
    return provider


def gateways_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(SqlAlchemyDialogCommandGateway, provides=DialogCommandGateway)
    provider.provide(SQLAlchemyTransactionManager, provides=TransactionManager)
    provider.provide(LangchainVectorStoreGateway, provides=DocumentCommandGateway)
    provider.provide(AiobotocoreDocumentStorage, provides=DocumentStorage)
    return provider


def application_ports_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(LangChainQuestionAnsweringPort, provides=QuestionAnsweringPort)
    provider.provide(TaskIQTaskScheduler, provides=TaskScheduler)
    provider.provide(get_file_processor_factory)
    return provider


def domain_ports_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(UUID4DocumentIDGenerator, provides=DocumentIDGenerator)
    provider.provide(UUID4ChunkIDGenerator, provides=ChunkIDGenerator)
    provider.provide(UUID4DialogIDGenerator, provides=DialogIDGenerator)
    provider.provide(SemanticTextSplitter, provides=TextSplitter)
    provider.provide(DocumentService)
    provider.provide(DialogService)
    return provider


def interactors_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide_all(
        AnswerTheQuestionCommandHandler, CreateDocumentCommandHandler, RetrievalAugmentationForDocumentCommandHandler
    )
    return provider


def setup_providers() -> Iterable[Provider]:
    return (
        configs_provider(),
        db_provider(),
        domain_ports_provider(),
        gateways_provider(),
        application_ports_provider(),
        interactors_provider(),
        FastapiProvider(),
        cache_provider(),
    )
