import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, cast, override

from langchain_core.documents import Document as LangchainDocument
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from clever_faq.application.common.ports.document.document_command_gateway import DocumentCommandGateway
from clever_faq.domain.document.entities.chunk import Chunk
from clever_faq.domain.document.entities.document import Document
from clever_faq.domain.document.values.document_name import DocumentName
from clever_faq.domain.document.values.document_text import DocumentText
from clever_faq.domain.document.values.document_type import DocumentType
from clever_faq.infrastructure.errors.persistence import EntityAddError, RepoError

if TYPE_CHECKING:
    from clever_faq.domain.document.values.chunk_id import ChunkID

logger: Final[logging.Logger] = logging.getLogger(__name__)


class LangchainVectorStoreGateway(DocumentCommandGateway):
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: Embeddings,
    ) -> None:
        self._vector_store: Final[VectorStore] = vector_store
        self._embedding_model: Final[Embeddings] = embedding_model

    @override
    async def add(self, document: Document) -> None:
        try:
            logger.info("Adding document %s to vector store", document.id)

            langchain_docs: list[LangchainDocument] = [
                LangchainDocument(
                    page_content=str(chunk_text.text),
                    metadata={
                        "document_id": str(document.id),
                        "document_title": str(document.name),
                        "created_at": datetime.now(UTC).isoformat(),
                        "updated_at": datetime.now(UTC).isoformat(),
                        "document_type": document.type.value,
                    },
                    id=str(chunk_text.id),
                )
                for chunk_text in document.chunks
            ]

            # Добавляем документы в векторное хранилище
            await self._vector_store.aadd_documents(langchain_docs)

        except Exception as e:
            logger.exception("Vector store insert failed")
            msg = "Saving to database failed"
            raise EntityAddError(msg) from e

    @override
    async def search_similar_by_text(self, text: DocumentText, count_of_similar: int) -> Iterable[Document]:
        try:
            langchain_documents: list[LangchainDocument] = await self._vector_store.asimilarity_search(
                query=text.value,
                k=count_of_similar,
            )

            return [
                Document(
                    id=langchain_document.metadata["document_id"],
                    name=DocumentName(langchain_document.metadata["document_title"]),
                    chunks=[
                        Chunk(
                            text=DocumentText(langchain_document.page_content),
                            id=cast("ChunkID", langchain_document.id),
                        )
                    ],
                    type=DocumentType(langchain_document.metadata["document_type"]),
                )
                for langchain_document in langchain_documents
            ]

        except Exception as e:
            logger.exception("Vector store search failed")
            msg = "Search failed"
            raise RepoError(msg) from e
