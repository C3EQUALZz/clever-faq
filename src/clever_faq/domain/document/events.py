from dataclasses import dataclass

from clever_faq.domain.common.events import BaseDomainEvent
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_name import DocumentName


@dataclass(frozen=True, slots=True, eq=False)
class DocumentNameChangedEvent(BaseDomainEvent):
    document_id: DocumentID
    new_document_name: DocumentName
