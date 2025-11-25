from typing import TYPE_CHECKING, Final

from dishka import AsyncContainer
from vkbottle.bot import BotLabeler, Message

from clever_faq.application.commands.questions.answer_the_question import (
    AnswerTheQuestionCommand,
    AnswerTheQuestionCommandHandler,
)

if TYPE_CHECKING:
    from clever_faq.application.common.views.questions import AnswerTheQuestionView

labeler: Final[BotLabeler] = BotLabeler()


@labeler.private_message()
async def answer_on_message(message: Message, container: AsyncContainer) -> None:
    async with container() as scoped_container:
        interactor: AnswerTheQuestionCommandHandler = await scoped_container.get(AnswerTheQuestionCommandHandler)
        command: AnswerTheQuestionCommand = AnswerTheQuestionCommand(
            question=message.text,
        )
        view: AnswerTheQuestionView = await interactor(command)

        message.reply(message=view.answer)
