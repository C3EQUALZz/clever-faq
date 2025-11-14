import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, overload

from clever_faq.domain.common.services.base import DomainService
from clever_faq.domain.document.entities.document import Document
from clever_faq.domain.document.events import DocumentNameChangedEvent
from clever_faq.domain.document.ports.document_id_generator import DocumentIDGenerator
from clever_faq.domain.document.ports.text_splitter import TextSplitter
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_name import DocumentName
from clever_faq.domain.document.values.document_text import DocumentText
from clever_faq.domain.document.values.document_type import DocumentType

if TYPE_CHECKING:
    from clever_faq.domain.document.entities.chunk import Chunk

logger: Final[logging.Logger] = logging.getLogger(__name__)


class DocumentService(DomainService):
    def __init__(
        self,
        text_splitter: TextSplitter,
        document_id_generator: DocumentIDGenerator,
    ) -> None:
        super().__init__()
        self._text_splitter: Final[TextSplitter] = text_splitter
        self._document_id_generator: Final[DocumentIDGenerator] = document_id_generator

    @overload
    def create_document(
        self,
        name: DocumentName,
        text: DocumentText,
        doc_type: DocumentType,
    ) -> Document: ...

    @overload
    def create_document(
        self, name: DocumentName, text: DocumentText, doc_type: DocumentType, document_id: DocumentID
    ) -> Document: ...

    def create_document(
        self,
        name: DocumentName,
        text: DocumentText,
        doc_type: DocumentType,
        document_id: DocumentID | None = None,
    ) -> Document:
        logger.info("Started creating document....")

        if document_id is None:
            document_id = self._document_id_generator()

        chunks: list[Chunk] = self._text_splitter.split_text(text)

        document: Document = Document(
            id=document_id,
            name=name,
            chunks=chunks,
            type=doc_type,
        )

        return document

    def change_document_name(self, document: Document, new_name: DocumentName) -> None:
        document.name = new_name
        document.updated_at = datetime.now(UTC)

        self._record_event(
            DocumentNameChangedEvent(
                document_id=document.id,
                new_document_name=str(document.name),
            )
        )
