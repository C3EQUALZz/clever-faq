from collections.abc import Iterable
from typing import Final

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from clever_faq.presentation.http.v1.routes.questions.ask_question.handlers import ask_question_router

questions_router: Final[APIRouter] = APIRouter(
    prefix="/questions",
    route_class=DishkaRoute,
    tags=["Question"],
)

sub_routers: Final[Iterable[APIRouter]] = (ask_question_router,)

for sub_router in sub_routers:
    questions_router.include_router(sub_router)
