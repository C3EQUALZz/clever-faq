from dataclasses import dataclass

from clever_faq.domain.common.entities.base_entity import BaseEntity
from clever_faq.domain.document.values.chunk_id import ChunkID
from clever_faq.domain.document.values.document_text import DocumentText


@dataclass(eq=False, kw_only=True)
class Chunk(BaseEntity[ChunkID]):
    text: DocumentText
