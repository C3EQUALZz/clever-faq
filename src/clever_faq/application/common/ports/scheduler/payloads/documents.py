from dataclasses import dataclass

from clever_faq.application.common.ports.scheduler.payloads.base import TaskPayload
from clever_faq.domain.document.values.document_id import DocumentID


@dataclass(frozen=True, slots=True, kw_only=True)
class RetrievalAugmentedGenerationPayload(TaskPayload):
    document_id: DocumentID
