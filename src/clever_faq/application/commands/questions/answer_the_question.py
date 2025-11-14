import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, final

from clever_faq.application.common.ports.dialog.dialog_command_gateway import DialogCommandGateway
from clever_faq.application.common.ports.question.question_answering_port import (
    MessageWithTokenDTO,
    QuestionAnsweringPort,
)
from clever_faq.application.common.ports.transaction_manager import TransactionManager
from clever_faq.domain.dialog.services.dialog_service import DialogService
from clever_faq.domain.dialog.values.message import Message

if TYPE_CHECKING:
    from clever_faq.domain.dialog.entities.dialog import Dialog

logger: Final[logging.Logger] = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class AnswerTheQuestionCommand:
    question: str


@final
class AnswerTheQuestionCommandHandler:
    def __init__(
        self,
        question_answering_port: QuestionAnsweringPort,
        dialog_service: DialogService,
        dialog_gateway: DialogCommandGateway,
        transaction_manager: TransactionManager,
    ) -> None:
        self._question_answering_port: Final[QuestionAnsweringPort] = question_answering_port
        self._dialog_service: Final[DialogService] = dialog_service
        self._dialog_gateway: Final[DialogCommandGateway] = dialog_gateway
        self._transaction_manager: Final[TransactionManager] = transaction_manager

    async def __call__(self, data: AnswerTheQuestionCommand) -> None:
        logger.info("Started answering question: %s", data.question)

        logger.info("Started validating question: %s", data.question)
        validated_question: Message = Message(data.question)
        logger.info("Question validated: %s", validated_question)

        logger.info("Started answering question: %s", data.question)
        answer_on_question: MessageWithTokenDTO = await self._question_answering_port.answer_the_question(
            question=validated_question,
        )
        logger.info("Got answer %s on question: %s", answer_on_question, validated_question)

        logger.info(
            "Started building new dialog for save in storage with question: %s, answer: %s, tokens: %s",
            data.question,
            answer_on_question.message,
            answer_on_question.tokens,
        )

        new_dialog: Dialog = self._dialog_service.create(
            question=validated_question, answer=answer_on_question.message, tokens=answer_on_question.tokens
        )

        logger.info("Started saving dialog: %s", new_dialog)
        await self._dialog_gateway.add(new_dialog)
        await self._transaction_manager.flush()
        await self._transaction_manager.commit()

        logger.info("Finished answering question: %s", data.question)
