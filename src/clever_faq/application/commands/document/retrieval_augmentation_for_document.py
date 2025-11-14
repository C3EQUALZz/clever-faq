import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, final
from uuid import UUID

from clever_faq.application.common.ports.document.document_command_gateway import DocumentCommandGateway
from clever_faq.application.common.ports.document.document_storage import DocumentDTO, DocumentStorage
from clever_faq.application.common.ports.document.file_processor_factory import FileProcessorFactory
from clever_faq.application.common.ports.transaction_manager import TransactionManager
from clever_faq.application.errors.document import DocumentNotFoundError
from clever_faq.domain.document.services.document import DocumentService
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_text import DocumentText

if TYPE_CHECKING:
    from clever_faq.application.common.ports.document.file_processor import FileProcessor
    from clever_faq.domain.document.entities.document import Document

logger: Final[logging.Logger] = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class RetrievalAugmentationForDocumentCommand:
    document_id: UUID


@final
class RetrievalAugmentationForDocumentCommandHandler:
    def __init__(
        self,
        file_processor_factory: FileProcessorFactory,
        document_service: DocumentService,
        document_command_gateway: DocumentCommandGateway,
        transaction_manager: TransactionManager,
        document_storage: DocumentStorage,
    ) -> None:
        self._file_processor_factory: Final[FileProcessorFactory] = file_processor_factory
        self._document_service: Final[DocumentService] = document_service
        self._document_command_gateway: Final[DocumentCommandGateway] = document_command_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._document_storage: Final[DocumentStorage] = document_storage

    async def __call__(self, data: RetrievalAugmentationForDocumentCommand) -> None:
        logger.info("Starting retrieval augmentation for document with id %s", data.document_id)

        document_id: DocumentID = DocumentID(data.document_id)

        document_dto: DocumentDTO | None = await self._document_storage.read_by_id(
            document_id=document_id,
        )

        if document_dto is None:
            msg = f"Document with id {document_id} not found"
            raise DocumentNotFoundError(msg)

        file_processor: FileProcessor = self._file_processor_factory.create(document_dto.document_type)
        logger.info("File processor is %s", file_processor)

        raw_data_from_text: str = file_processor.extract_text(file_bytes=document_dto.document_content)

        document_text: DocumentText = DocumentText(raw_data_from_text)

        new_document: Document = self._document_service.create_document(
            name=document_dto.document_name,
            text=document_text,
            document_id=document_dto.document_id,
            doc_type=document_dto.document_type,
        )

        logger.info("New document is %s", new_document.id)
        await self._document_command_gateway.add(new_document)
        await self._transaction_manager.flush()
        await self._transaction_manager.commit()

        logger.info("Finished retrieval augmentation for document with id %s", new_document.id)
