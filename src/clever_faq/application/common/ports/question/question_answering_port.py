from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from clever_faq.domain.dialog.values.message import Message
from clever_faq.domain.dialog.values.tokens import Tokens


@dataclass(frozen=True, slots=True, kw_only=True)
class MessageWithTokenDTO:
    message: Message
    tokens: Tokens


class QuestionAnsweringPort(Protocol):
    @abstractmethod
    async def answer_the_question(self, question: Message) -> MessageWithTokenDTO: ...
