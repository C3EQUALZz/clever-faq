from uuid import uuid4

import pytest

from clever_faq.application.commands.document.create_document import (
    CreateDocumentCommand,
    CreateDocumentCommandHandler,
)
from clever_faq.application.common.ports.document.document_storage import DocumentDTO, DocumentStorage
from clever_faq.application.common.ports.scheduler.payloads.documents import RetrievalAugmentedGenerationPayload
from clever_faq.application.common.ports.scheduler.task_id import TaskID, TaskKey
from clever_faq.application.common.ports.scheduler.task_scheduler import TaskScheduler
from clever_faq.application.common.views.document import CreateDocumentView
from clever_faq.domain.document.ports.document_id_generator import DocumentIDGenerator
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_type import DocumentType


@pytest.mark.asyncio
async def test_create_document_handler_stores_document_and_schedules_task(
    fake_document_id_generator: DocumentIDGenerator,
    fake_document_storage: DocumentStorage,
    fake_task_scheduler: TaskScheduler,
) -> None:
    document_id = DocumentID(uuid4())
    fake_document_id_generator.return_value = document_id  # type: ignore[attr-defined]

    expected_task_id = TaskID("retrieval_augmented_generation_document:123")
    fake_task_scheduler.make_task_id.return_value = expected_task_id  # type: ignore[attr-defined]

    handler = CreateDocumentCommandHandler(
        document_id_generator=fake_document_id_generator,
        document_storage=fake_document_storage,
        scheduler=fake_task_scheduler,
    )

    command = CreateDocumentCommand(
        name="Manual.pdf",
        content=b"binary",
        mime_type="application/pdf",
    )

    result = await handler(command)

    assert result == CreateDocumentView(document_id=document_id, task_id=expected_task_id)

    fake_document_storage.add.assert_awaited_once()
    stored_document: DocumentDTO = fake_document_storage.add.await_args.kwargs["document"]
    assert stored_document.document_id == document_id
    assert stored_document.document_name.value == command.name
    assert stored_document.document_type == DocumentType.PDF
    assert stored_document.document_content == command.content

    fake_task_scheduler.make_task_id.assert_called_once_with(
        key=TaskKey("retrieval_augmented_generation_document"),
        value=str(document_id),
    )

    fake_task_scheduler.schedule.assert_called_once()
    schedule_kwargs = fake_task_scheduler.schedule.call_args.kwargs
    assert schedule_kwargs["task_id"] == expected_task_id
    payload = schedule_kwargs["payload"]
    assert isinstance(payload, RetrievalAugmentedGenerationPayload)
    assert payload.document_id == document_id
