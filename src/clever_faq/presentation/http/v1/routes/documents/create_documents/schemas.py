from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateImageSchemaResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: Annotated[str, Field(description="ID for new task")]
    document_id: Annotated[UUID, Field(description="ID for new document")]
