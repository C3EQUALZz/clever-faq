from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateDocumentView:
    document_id: UUID
    task_id: str
