from collections.abc import Mapping
from typing import Final

from clever_faq.application.common.ports.document.file_processor import FileProcessor
from clever_faq.application.errors.document import UnknownMimeTypeError
from clever_faq.domain.document.values.document_type import DocumentType


def convert_mime_type_to_type_of_file(mime_type: str) -> DocumentType:
    if mime_type == "text/plain":
        return DocumentType.TXT

    if mime_type == "application/pdf":
        return DocumentType.PDF

    if mime_type == "application/docx":
        return DocumentType.DOCX

    if mime_type == "application/vnd.oasis.opendocument.text":
        return DocumentType.ODT

    if mime_type == "application/vnd.oasis.opendocument.presentation":
        return DocumentType.PPTX

    msg: str = f"Unknown mime type {mime_type}"

    raise UnknownMimeTypeError(msg)


class FileProcessorFactory:
    def __init__(self, processors_mapping: Mapping[DocumentType, FileProcessor]) -> None:
        self._processors_mapping: Final[Mapping[DocumentType, FileProcessor]] = processors_mapping

    def create(self, type_of_file: DocumentType) -> FileProcessor:
        result: FileProcessor | None = self._processors_mapping.get(type_of_file, None)

        if result is None:
            msg = f"Unknown mime type {type_of_file}"
            raise UnknownMimeTypeError(msg)

        return result
