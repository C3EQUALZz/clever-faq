from inspect import getdoc
from typing import TYPE_CHECKING, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from clever_faq.application.commands.questions.answer_the_question import (
    AnswerTheQuestionCommand,
    AnswerTheQuestionCommandHandler,
)
from clever_faq.presentation.http.v1.routes.questions.ask_question.schemas import (
    AskQuestionSchemaRequest,
    AskQuestionSchemaResponse,
)

if TYPE_CHECKING:
    from clever_faq.application.common.views.questions import AnswerTheQuestionView

ask_question_router: Final[APIRouter] = APIRouter(route_class=DishkaRoute, tags=["Questions"])


@ask_question_router.post(
    "/ask/",
    status_code=status.HTTP_201_CREATED,
    summary="Handler for answering question from user",
    description=getdoc(AnswerTheQuestionCommandHandler),
    response_model={},
)
async def ask_the_question_handler(
    request_schema: AskQuestionSchemaRequest, interactor: FromDishka[AnswerTheQuestionCommandHandler]
) -> AskQuestionSchemaResponse:
    command: AnswerTheQuestionCommand = AnswerTheQuestionCommand(
        question=request_schema.question,
    )

    view: AnswerTheQuestionView = await interactor(command)

    return AskQuestionSchemaResponse(
        answer=view.answer,
    )
