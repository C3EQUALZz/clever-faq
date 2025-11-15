from collections.abc import Iterable
from typing import Final

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from clever_faq.presentation.http.v1.routes.documents.create_documents.handlers import create_documents_router

documents_router: Final[APIRouter] = APIRouter(
    route_class=DishkaRoute,
    tags=["Document"],
    prefix="/documents",
)

sub_routers: Final[Iterable[APIRouter]] = (create_documents_router,)

for sub_router in sub_routers:
    documents_router.include_router(sub_router)
