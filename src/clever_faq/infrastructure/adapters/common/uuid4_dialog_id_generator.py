from typing import cast, override
from uuid import uuid4

from clever_faq.domain.dialog.ports.dialog_id_generator import DialogIDGenerator
from clever_faq.domain.dialog.values.dialog_id import DialogID


class UUID4DialogIDGenerator(DialogIDGenerator):
    @override
    def __call__(self) -> DialogID:
        return cast("DialogID", uuid4())
