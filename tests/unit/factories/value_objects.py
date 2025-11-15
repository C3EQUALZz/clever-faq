from dataclasses import dataclass

from clever_faq.domain.common.values.base import BaseValueObject


@dataclass(frozen=True, slots=True, repr=True)
class SingleFieldVO(BaseValueObject):
    value: int

    def _validate(self) -> None: ...

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True, repr=True)
class MultiFieldVO(BaseValueObject):
    value1: int
    value2: str

    def _validate(self) -> None: ...

    def __str__(self) -> str:
        return str(self.value1) + str(self.value2)


def create_single_field_vo(value: int = 1) -> SingleFieldVO:
    return SingleFieldVO(value)


def create_multi_field_vo(value1: int = 1, value2: str = "Alice") -> MultiFieldVO:
    return MultiFieldVO(value1, value2)
