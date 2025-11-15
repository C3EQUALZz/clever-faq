from typing import Literal

from pydantic import BaseModel, Field


class OpenAIEmbeddingsSettings(BaseModel):
    """Parameters for embedding model invocations."""

    model: str = Field(
        default="text-embedding-3-large",
        description="Embedding model identifier.",
    )
    dimensions: int | None = Field(
        default=None,
        description="Optional number of embedding dimensions to request.",
        ge=1,
    )
    timeout: float = Field(
        default=30.0,
        ge=0.0,
        description="HTTP request timeout for embedding calls (seconds).",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Number of retries for embedding requests.",
    )
    chunk_size: int = Field(
        default=64,
        ge=1,
        description="Chunk size used when sending texts for embedding.",
    )
    langsmith_tracing: bool = Field(
        alias="LANGSMITH_TRACING",
    )
    langsmith_api_key: str = Field(
        alias="LANGSMITH_API_KEY",
    )


class OpenAIChatSettings(BaseModel):
    """Parameters for chat/completions model invocations."""

    model: str = Field(
        default="gpt-4o-mini",
        description="Chat/completions model identifier.",
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for creative control.",
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Top-p nucleus sampling parameter.",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        description="Maximum tokens to generate in a response.",
    )
    timeout: float = Field(
        default=60.0,
        ge=0.0,
        description="HTTP request timeout for chat calls (seconds).",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Number of retries for chat requests.",
    )
    response_format: Literal["text", "json_object"] = Field(
        default="text",
        description="Desired response serialization format.",
    )


class OpenAISettings(BaseModel):
    """Top-level OpenAI configuration with separate chat/embedding tunables."""

    api_key: str = Field(
        alias="OPENAI_API_KEY",
        description="Secret key for authenticating with OpenAI APIs.",
    )
    organization: str | None = Field(
        default=None,
        alias="OPENAI_ORGANIZATION",
        description="Optional organization identifier.",
    )
    project: str | None = Field(
        default=None,
        alias="OPENAI_PROJECT",
        description="Optional project identifier.",
    )
    base_url: str | None = Field(
        default=None,
        alias="OPENAI_BASE_URL",
        description="Override for OpenAI-compatible API base URL.",
    )
    embeddings: OpenAIEmbeddingsSettings = Field(
        default_factory=OpenAIEmbeddingsSettings,
        description="Embedding-model specific settings.",
    )
    chat: OpenAIChatSettings = Field(
        default_factory=OpenAIChatSettings,
        description="Chat-model specific settings.",
    )
