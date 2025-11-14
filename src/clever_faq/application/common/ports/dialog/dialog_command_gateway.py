from abc import abstractmethod
from typing import Protocol

from clever_faq.domain.dialog.entities.dialog import Dialog
from clever_faq.domain.dialog.values.dialog_id import DialogID


class DialogCommandGateway(Protocol):
    @abstractmethod
    async def add(self, dialog: Dialog) -> None: ...

    @abstractmethod
    async def delete_by_id(self, dialog_id: DialogID) -> None: ...

    @abstractmethod
    async def read_by_id(self, dialog_id: DialogID) -> Dialog | None: ...
