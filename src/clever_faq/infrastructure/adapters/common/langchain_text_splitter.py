import logging
from typing import TYPE_CHECKING, Final, override

from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter

from clever_faq.domain.document.entities.chunk import Chunk
from clever_faq.domain.document.ports.chunk_id_generator import ChunkIDGenerator
from clever_faq.domain.document.ports.text_splitter import TextSplitter
from clever_faq.domain.document.values.document_text import DocumentText

if TYPE_CHECKING:
    from langchain_core.documents import Document as LangchainDocument

logger: Final[logging.Logger] = logging.getLogger(__name__)

MAX_CHUNK_LENGTH: Final[int] = 512


class SemanticTextSplitter(TextSplitter):
    def __init__(self, embeddings: Embeddings, chunk_id_generator: ChunkIDGenerator) -> None:
        self._semantic_splitter: Final[SemanticChunker] = SemanticChunker(
            embeddings, breakpoint_threshold_type="gradient"
        )
        self._pre_splitter: Final[RecursiveCharacterTextSplitter] = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        self._chunk_id_generator: Final[ChunkIDGenerator] = chunk_id_generator

    @override
    def split_text(self, text: DocumentText) -> list[Chunk]:
        pre_documents: list[LangchainDocument] = self._pre_splitter.create_documents([text.value])

        final_chunks: list[Chunk] = []
        for doc in pre_documents:
            semantic_docs = self._semantic_splitter.create_documents([doc.page_content])

            for chunk in semantic_docs:
                if len(chunk.page_content) > MAX_CHUNK_LENGTH:
                    sub_chunks = self._pre_splitter.split_text(chunk.page_content)
                    final_chunks.extend(
                        [Chunk(text=DocumentText(c), id=self._chunk_id_generator()) for c in sub_chunks]
                    )
                else:
                    final_chunks.append(Chunk(text=DocumentText(chunk.page_content), id=self._chunk_id_generator()))

        logger.debug("Split text into %d chunks", len(final_chunks))

        return final_chunks
