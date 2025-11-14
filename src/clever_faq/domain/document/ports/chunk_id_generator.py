from abc import abstractmethod
from typing import Protocol

from clever_faq.domain.document.values.chunk_id import ChunkID


class ChunkIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> ChunkID: ...
