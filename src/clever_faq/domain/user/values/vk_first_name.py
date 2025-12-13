from dataclasses import dataclass
from typing import Final, override

from clever_faq.domain.common.values.base import BaseValueObject
from clever_faq.domain.user.errors import BadVkUserError

VK_NAME_MAX_LENGTH: Final[int] = 32


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class VkUserFirstName(BaseValueObject):
    value: str

    @override
    def _validate(self) -> None:
        if self.value.strip() == "":
            msg = "Vk user first name cannot be empty"
            raise BadVkUserError(msg)

        if len(self.value) > VK_NAME_MAX_LENGTH:
            msg = f"Bad user first name, length must be less than 32 characters, current length is {len(self.value)}"
            raise BadVkUserError(msg)

    @override
    def __str__(self) -> str:
        return self.value
