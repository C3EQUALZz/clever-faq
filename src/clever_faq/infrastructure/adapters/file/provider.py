from clever_faq.application.common.ports.document.file_processor_factory import FileProcessorFactory
from clever_faq.domain.document.values.document_type import DocumentType
from clever_faq.infrastructure.adapters.file.docx import DocxFileProcessor
from clever_faq.infrastructure.adapters.file.odt import OdtFileProcessor
from clever_faq.infrastructure.adapters.file.pdf import PdfFileProcessor
from clever_faq.infrastructure.adapters.file.powerpoint import PptxFileProcessor
from clever_faq.infrastructure.adapters.file.text import TextFileProcessor


def get_file_processor_factory() -> FileProcessorFactory:
    return FileProcessorFactory(
        processors_mapping={
            DocumentType.TXT: TextFileProcessor(),
            DocumentType.PDF: PdfFileProcessor(),
            DocumentType.DOCX: DocxFileProcessor(),
            DocumentType.ODT: OdtFileProcessor(),
            DocumentType.PPTX: PptxFileProcessor(),
        }
    )
