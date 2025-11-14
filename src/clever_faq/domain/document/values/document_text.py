from dataclasses import dataclass
from typing import override

from clever_faq.domain.common.values.base import BaseValueObject
from clever_faq.domain.document.errors import BadDocumentTextError


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class DocumentText(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:
        if self.value.isspace() or self.value == "":
            msg = "Document text cannot be empty"
            raise BadDocumentTextError(msg)

    @override
    def __str__(self) -> str:
        return self.value
