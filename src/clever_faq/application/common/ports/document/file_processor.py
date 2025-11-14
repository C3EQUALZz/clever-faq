from abc import abstractmethod
from typing import Protocol


class FileProcessor(Protocol):
    @abstractmethod
    async def extract_text(self, file_bytes: bytes) -> str: ...
