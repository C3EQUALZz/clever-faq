from typing import Final

from clever_faq.domain.common.services.base import DomainService
from clever_faq.domain.dialog.entities.dialog import Dialog
from clever_faq.domain.dialog.ports.dialog_id_generator import DialogIDGenerator
from clever_faq.domain.dialog.values.message import Message
from clever_faq.domain.dialog.values.tokens import Tokens


class DialogService(DomainService):
    def __init__(
        self,
        dialog_id_generator: DialogIDGenerator,
    ) -> None:
        super().__init__()
        self._dialog_id_generator: Final[DialogIDGenerator] = dialog_id_generator

    def create(self, question: Message, answer: Message, tokens: Tokens) -> Dialog:
        new_dialog: Dialog = Dialog(
            question=question,
            tokens=tokens,
            id=self._dialog_id_generator(),
            answer=answer,
        )

        return new_dialog
