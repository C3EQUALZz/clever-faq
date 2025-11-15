import io
import logging
from typing import Final, override

import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException

from clever_faq.application.common.ports.document.file_processor import FileProcessor
from clever_faq.infrastructure.errors.file import CantReadFileError

logger: Final[logging.Logger] = logging.getLogger(__name__)


class PdfFileProcessor(FileProcessor):
    @override
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            logger.info("Started processing pdf file")
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                extracted_text: str = "\n".join(page.extract_text() for page in pdf.pages)
                logger.info("Finished processing pdf file")
                return extracted_text
        except PdfminerException as e:
            logger.exception("Failed to process pdf file")
            msg = "Failed to process pdf file"
            raise CantReadFileError(msg) from e
