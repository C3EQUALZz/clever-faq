from abc import abstractmethod
from typing import Protocol

from clever_faq.domain.dialog.values.dialog_id import DialogID


class DialogIDGenerator(Protocol):
    @abstractmethod
    def __call__(self) -> DialogID: ...
