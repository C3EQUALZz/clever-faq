from abc import abstractmethod
from typing import Protocol

from clever_faq.domain.document.values.document_id import DocumentID


class DocumentIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> DocumentID: ...
