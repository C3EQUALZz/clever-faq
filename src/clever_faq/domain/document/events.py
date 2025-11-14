from dataclasses import dataclass
from uuid import UUID

from clever_faq.domain.common.events import BaseDomainEvent


@dataclass(frozen=True, slots=True, eq=False)
class DocumentNameChangedEvent(BaseDomainEvent):
    document_id: UUID
    new_document_name: str
