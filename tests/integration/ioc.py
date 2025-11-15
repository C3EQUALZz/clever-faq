from collections.abc import Iterable
from typing import Final

from dishka import Provider, Scope
from dishka.integrations.fastapi import FastapiProvider
from langchain_core.embeddings import Embeddings, FakeEmbeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.fake_chat_models import FakeChatModel
from sqlalchemy.ext.asyncio import AsyncSession

from clever_faq.infrastructure.persistence.provider import (
    get_engine,
    get_s3_client,
    get_s3_session,
    get_session,
    get_sessionmaker,
    get_vector_store,
)
from clever_faq.setup.ioc import (
    application_ports_provider,
    cache_provider,
    configs_provider,
    domain_ports_provider,
    gateways_provider,
    interactors_provider,
)


def fake_embeddings() -> Embeddings:
    return FakeEmbeddings(size=512)


def fake_chat_model() -> BaseChatModel:
    return FakeChatModel()


def db_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(get_vector_store)
    provider.provide(fake_embeddings)
    provider.provide(fake_chat_model)
    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_sessionmaker, scope=Scope.APP)
    provider.provide(get_session, provides=AsyncSession)
    provider.provide(get_s3_session)
    provider.provide(get_s3_client)
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
