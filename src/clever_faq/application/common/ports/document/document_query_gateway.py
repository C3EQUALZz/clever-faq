from abc import abstractmethod
from typing import Protocol

from clever_faq.domain.document.entities.document import Document
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_name import DocumentName


class DocumentQueryGateway(Protocol):
    @abstractmethod
    async def read_by_id(self, document_id: DocumentID) -> Document | None: ...

    @abstractmethod
    async def read_by_name(self, document_name: DocumentName) -> Document | None: ...
