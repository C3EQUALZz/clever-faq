import re
from dataclasses import dataclass
from typing import Final, override

from clever_faq.domain.common.values.base import BaseValueObject
from clever_faq.domain.dialog.errors import BadMessageError

_PROFANITY_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:\b|^)(?:х[уy][йи](?:н[яе]|ло)?|пизд\w*|еб[ауеёиыо]\w*|сука|бля[тд]\w*)",
    re.IGNORECASE,
)


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class Message(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:
        if not self.value or not self.value.strip():
            msg = "Message cannot be empty"
            raise BadMessageError(msg)

        if _PROFANITY_PATTERN.search(self.value):
            msg = "Message contains inappropriate language"
            raise BadMessageError(msg)

    @override
    def __str__(self) -> str:
        return self.value
