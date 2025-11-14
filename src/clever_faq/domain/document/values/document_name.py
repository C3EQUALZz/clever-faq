from dataclasses import dataclass
from typing import override

from clever_faq.domain.common.values.base import BaseValueObject
from clever_faq.domain.document.errors import BadDocumentNameError


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class DocumentName(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:
        if self.value == "" or self.value.isspace():
            msg: str = "Document name cannot be empty"
            raise BadDocumentNameError(msg)

    @override
    def __str__(self) -> str:
        return self.value
