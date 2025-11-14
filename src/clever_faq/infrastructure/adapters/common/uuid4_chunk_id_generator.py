import uuid
from typing import cast, override

from clever_faq.domain.document.ports.chunk_id_generator import ChunkIDGenerator
from clever_faq.domain.document.values.chunk_id import ChunkID


class UUID4ChunkIDGenerator(ChunkIDGenerator):
    @override
    def __call__(self) -> ChunkID:
        return cast("ChunkID", uuid.uuid4())
