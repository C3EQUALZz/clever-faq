from dataclasses import dataclass
from typing import override

from clever_faq.domain.common.values.base import BaseValueObject


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class Tokens(BaseValueObject):
    value: int

    @override
    def _validate(self) -> None: ...

    @override
    def __str__(self) -> str:
        return str(self.value)
