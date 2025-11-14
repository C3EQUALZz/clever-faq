from dataclasses import dataclass

from clever_faq.domain.common.entities.base_aggregate import BaseAggregateRoot
from clever_faq.domain.dialog.values.dialog_id import DialogID
from clever_faq.domain.dialog.values.message import Message
from clever_faq.domain.dialog.values.tokens import Tokens


@dataclass(eq=False, kw_only=True)
class Dialog(BaseAggregateRoot[DialogID]):
    question: Message
    answer: Message
    tokens: Tokens
