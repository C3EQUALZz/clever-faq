import random
import string
from inspect import getdoc
from typing import TYPE_CHECKING, Annotated, Final

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, File, UploadFile, status

from clever_faq.application.commands.document.create_document import CreateDocumentCommand, CreateDocumentCommandHandler
from clever_faq.presentation.errors.document import BadFileFormatError
from clever_faq.presentation.http.v1.common.exception_handler import ExceptionSchema
from clever_faq.presentation.http.v1.routes.documents.create_documents.schemas import CreateImageSchemaResponse

if TYPE_CHECKING:
    from clever_faq.application.common.views.document import CreateDocumentView

create_documents_router: Final[APIRouter] = APIRouter(
    tags=["Document"],
    route_class=DishkaRoute,
)


@create_documents_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateImageSchemaResponse,
    summary="Create Document in system",
    description=getdoc(CreateDocumentCommandHandler),
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def create_document_handler(
    image: Annotated[UploadFile, File(description="A file for uploading to backend")],
    interactor: FromDishka[CreateDocumentCommandHandler],
) -> CreateImageSchemaResponse:
    if image.content_type is None:
        msg = "Unknown content type"
        raise BadFileFormatError(msg)

    if not image.content_type.startswith("image/"):
        msg = f"Invalid content type {image.content_type}"
        raise BadFileFormatError(msg)

    letters: str = string.ascii_lowercase
    result_str: str = "".join(random.choice(letters) for _ in range(20))  # nosec B311

    content: bytes = await image.read()
    filename: str = image.filename if image.filename is not None else result_str

    command: CreateDocumentCommand = CreateDocumentCommand(
        name=filename,
        content=content,
        mime_type=image.content_type,
    )

    view: CreateDocumentView = await interactor(command)

    return CreateImageSchemaResponse(
        task_id=view.task_id,
        document_id=view.document_id,
    )
