from dataclasses import dataclass

from clever_faq.domain.common.entities.base_aggregate import BaseAggregateRoot
from clever_faq.domain.document.entities.chunk import Chunk
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_name import DocumentName
from clever_faq.domain.document.values.document_type import DocumentType


@dataclass(eq=False, kw_only=True)
class Document(BaseAggregateRoot[DocumentID]):
    name: DocumentName
    chunks: list[Chunk]
    type: DocumentType
