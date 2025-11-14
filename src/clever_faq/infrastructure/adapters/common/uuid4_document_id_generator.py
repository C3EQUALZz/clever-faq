import uuid
from typing import cast, override

from clever_faq.domain.document.ports.document_id_generator import DocumentIDGenerator
from clever_faq.domain.document.values.document_id import DocumentID


class UUID4DocumentIDGenerator(DocumentIDGenerator):
    @override
    def __call__(self) -> DocumentID:
        return cast("DocumentID", uuid.uuid4())
