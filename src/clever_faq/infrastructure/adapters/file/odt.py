import logging
from io import BytesIO
from typing import Final, override

from odf import teletype, text
from odf.opendocument import OpenDocument, load

from clever_faq.application.common.ports.document.file_processor import FileProcessor
from clever_faq.infrastructure.errors.file import CantReadFileError

logger: Final[logging.Logger] = logging.getLogger(__name__)


class OdtFileProcessor(FileProcessor):
    @override
    def extract_text(self, file_bytes: bytes) -> str:
        logger.info("Started processing odt file")
        try:
            byte_stream: BytesIO = BytesIO(file_bytes)
            doc: OpenDocument = load(byte_stream)
            extracted_text: str = "\n".join(
                teletype.extractText(paragraph) for paragraph in doc.getElementsByType(text.P)
            )
        except Exception as e:
            logger.exception("Error processing ODT file")
            msg = "Invalid ODT file format"
            raise CantReadFileError(msg) from e
        else:
            logger.info("Finished processing odt file")
            return extracted_text
