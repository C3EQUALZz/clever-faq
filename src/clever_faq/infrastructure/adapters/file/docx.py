import io
import logging
from typing import Final, override

from docx import Document

from clever_faq.application.common.ports.document.file_processor import FileProcessor
from clever_faq.infrastructure.errors.file import CantReadFileError

logger: Final[logging.Logger] = logging.getLogger(__name__)


class DocxFileProcessor(FileProcessor):
    @override
    def extract_text(self, file_bytes: bytes) -> str:
        logger.info("Started extracting text from Docx file")
        try:
            doc: Document = Document(io.BytesIO(file_bytes))
            extracted_text: str = "\n".join(para.text for para in doc.paragraphs)
        except ValueError as e:
            logger.exception("Error processing docx file")
            msg = "Can't read this docx file"
            raise CantReadFileError(msg) from e
        except Exception as e:
            logger.exception("Error processing docx file")
            msg = "Can't read this docx file"
            raise CantReadFileError(msg) from e
        else:
            return extracted_text
