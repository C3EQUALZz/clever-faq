from typing import override

from clever_faq.application.common.ports.document.file_processor import FileProcessor
from clever_faq.infrastructure.errors.file import CantReadFileError


class TextFileProcessor(FileProcessor):
    @override
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError as err:
            msg = "Can't decode binary text to utf-8"
            raise CantReadFileError(msg) from err
