from abc import abstractmethod
from collections.abc import Iterable
from typing import Protocol

from clever_faq.domain.document.entities.document import Document
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_name import DocumentName
from clever_faq.domain.document.values.document_text import DocumentText


class DocumentCommandGateway(Protocol):
    @abstractmethod
    async def add(self, document: Document) -> None: ...

    @abstractmethod
    async def read_by_id(self, document_id: DocumentID) -> Document | None: ...

    @abstractmethod
    async def delete_by_id(self, document_id: DocumentID) -> None: ...

    @abstractmethod
    async def search_similar_by_text(self, text: DocumentText, count_of_similar: int) -> Iterable[Document]: ...

    @abstractmethod
    async def read_by_name(self, document_name: DocumentName) -> Document | None: ...
