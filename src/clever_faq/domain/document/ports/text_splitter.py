from abc import abstractmethod
from typing import Protocol

from clever_faq.domain.document.entities.chunk import Chunk
from clever_faq.domain.document.values.document_text import DocumentText


class TextSplitter(Protocol):
    @abstractmethod
    def split_text(self, text: DocumentText) -> list[Chunk]: ...
