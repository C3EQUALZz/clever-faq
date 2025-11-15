import logging
from typing import Annotated, Final

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq import AsyncBroker, Context, TaskiqDepends
from taskiq.depends.progress_tracker import ProgressTracker, TaskState

from clever_faq.application.commands.document.retrieval_augmentation_for_document import (
    RetrievalAugmentationForDocumentCommand,
    RetrievalAugmentationForDocumentCommandHandler,
)
from clever_faq.application.errors.document import DocumentNotFoundError
from clever_faq.domain.common.errors import AppError
from clever_faq.infrastructure.scheduler.tasks.schemas import RetrievalAugmentationForDocumentRequestTask

logger: Final[logging.Logger] = logging.getLogger(__name__)


@inject(patch_module=True)
async def retrieval_augmentation_for_document_task(
    request_schema: RetrievalAugmentationForDocumentRequestTask,
    context: Annotated[Context, TaskiqDepends()],
    progress_tracker: Annotated[ProgressTracker, TaskiqDepends()],
    interactor: FromDishka[RetrievalAugmentationForDocumentCommandHandler],
) -> None:
    await progress_tracker.set_progress(
        state=TaskState.STARTED, meta=f"Started retrieval_augmentation with id {request_schema.document_id}"
    )

    logger.info(
        "Running task: %s with id: %s",
        context.message.task_name,
        context.message.task_id,
    )

    try:
        command: RetrievalAugmentationForDocumentCommand = RetrievalAugmentationForDocumentCommand(
            document_id=request_schema.document_id,
        )

        await interactor(data=command)

        logger.info(
            "Finished task: %s with id: %s",
            context.message.task_name,
            context.message.task_id,
        )

        await progress_tracker.set_progress(state=TaskState.SUCCESS)

    except DocumentNotFoundError:
        logger.exception(
            "Document with id %s not found",
            request_schema.document_id,
        )
        await progress_tracker.set_progress(state=TaskState.FAILURE)
        context.reject()

    except (AppError, Exception):
        logger.exception("App error was occurred")
        await progress_tracker.set_progress(state=TaskState.FAILURE)
        context.reject()


def setup_documents_task(broker: AsyncBroker) -> None:
    logger.info("Setup tasks")

    broker.register_task(
        func=retrieval_augmentation_for_document_task,
        retry_on_error=True,
        max_retries=3,
        delay=15,
        task_name="retrieval_augmented_generation_document",
    )
