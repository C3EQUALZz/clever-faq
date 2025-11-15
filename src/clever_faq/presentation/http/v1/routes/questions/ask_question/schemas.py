from typing import Annotated

from pydantic import BaseModel, Field


class AskQuestionSchemaRequest(BaseModel):
    question: Annotated[str, Field(min_length=1)]


class AskQuestionSchemaResponse(BaseModel):
    answer: Annotated[str, Field(min_length=1)]
