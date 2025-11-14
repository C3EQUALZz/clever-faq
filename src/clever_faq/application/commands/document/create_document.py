import asyncio
import logging
from asyncio import Task
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, final

from clever_faq.application.common.ports.document.document_storage import DocumentDTO, DocumentStorage
from clever_faq.application.common.ports.document.file_processor_factory import convert_mime_type_to_type_of_file
from clever_faq.application.common.ports.scheduler.payloads.documents import RetrievalAugmentedGenerationPayload
from clever_faq.application.common.ports.scheduler.task_id import TaskID, TaskKey
from clever_faq.application.common.ports.scheduler.task_scheduler import TaskScheduler
from clever_faq.application.common.views.document import CreateDocumentView
from clever_faq.domain.document.ports.document_id_generator import DocumentIDGenerator
from clever_faq.domain.document.values.document_name import DocumentName

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from clever_faq.domain.document.values.document_id import DocumentID
    from clever_faq.domain.document.values.document_type import DocumentType

logger: Final[logging.Logger] = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateDocumentCommand:
    name: str
    content: bytes
    mime_type: str


@final
class CreateDocumentCommandHandler:
    def __init__(
        self,
        document_id_generator: DocumentIDGenerator,
        document_storage: DocumentStorage,
        scheduler: TaskScheduler,
    ) -> None:
        self._document_storage: Final[DocumentStorage] = document_storage
        self._scheduler: Final[TaskScheduler] = scheduler
        self._document_id_generator: Final[DocumentIDGenerator] = document_id_generator

    async def __call__(self, data: CreateDocumentCommand) -> CreateDocumentView:
        logger.info("Starting add document from file %s", data.name)

        file_name: DocumentName = DocumentName(data.name)
        type_of_file: DocumentType = convert_mime_type_to_type_of_file(data.mime_type)
        document_id: DocumentID = self._document_id_generator()

        document_dto_for_save_in_storage: DocumentDTO = DocumentDTO(
            document_id=document_id,
            document_name=file_name,
            document_content=data.content,
            document_type=type_of_file,
        )

        await self._document_storage.add(
            file_dto=document_dto_for_save_in_storage,
        )

        task_id: TaskID = self._scheduler.make_task_id(
            key=TaskKey("retrieval_augmented_generation_document"),
            value=str(document_id),
        )

        background_tasks: set[Task[None]] = set()

        coroutine: Coroutine[Any, Any, None] = self._scheduler.schedule(
            task_id=task_id,
            payload=RetrievalAugmentedGenerationPayload(
                document_id=document_id,
            ),
        )

        task: Task[None] = asyncio.create_task(coroutine)
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

        logger.info("Send document with id: %s for retrieval_augmented_generation, task id: %s", document_id, task_id)

        return CreateDocumentView(
            document_id=document_id,
            task_id=task_id,
        )
