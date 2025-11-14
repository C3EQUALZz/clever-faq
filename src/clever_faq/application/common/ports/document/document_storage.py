from abc import abstractmethod
from dataclasses import dataclass
from typing import NewType, Protocol
from uuid import UUID

from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_name import DocumentName
from clever_faq.domain.document.values.document_type import DocumentType

FileID = NewType("FileID", UUID)


@dataclass(frozen=True, slots=True, kw_only=True)
class DocumentDTO:
    document_id: DocumentID
    document_name: DocumentName
    document_type: DocumentType
    document_content: bytes


class DocumentStorage(Protocol):
    @abstractmethod
    async def add(self, file_dto: DocumentDTO) -> None: ...

    @abstractmethod
    async def read_by_id(self, file_id: FileID) -> DocumentDTO | None: ...
