from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class RetrievalAugmentationForDocumentRequestTask(BaseModel):
    document_id: Annotated[UUID, Field(description="Unique document id for processing")]
