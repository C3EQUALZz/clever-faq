from collections.abc import AsyncIterator

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from clever_faq.setup.config.openai import OpenAISettings


async def get_embeddings(config: OpenAISettings) -> AsyncIterator[Embeddings]:
    yield OpenAIEmbeddings(
        model=config.embeddings.model,
        api_key=config.api_key,
        organization=config.organization,
        dimensions=config.embeddings.dimensions,
        timeout=config.embeddings.timeout,
        max_retries=config.embeddings.max_retries,
        base_url=config.base_url,
        chunk_size=config.embeddings.chunk_size,
    )


async def get_chat_model(config: OpenAISettings) -> AsyncIterator[BaseChatModel]:
    yield ChatOpenAI(
        model=config.chat.model,
        api_key=config.api_key,
        organization=config.organization,
        temperature=config.chat.temperature,
        top_p=config.chat.top_p,
        max_tokens=config.chat.max_tokens,
        timeout=config.chat.timeout,
        max_retries=config.chat.max_retries,
        base_url=config.base_url,
        response_format=config.chat.response_format,
    )
