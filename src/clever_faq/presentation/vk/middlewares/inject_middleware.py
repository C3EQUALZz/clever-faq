from typing import override

from dishka import AsyncContainer
from vkbottle import ABCView, BaseMiddleware
from vkbottle.bot import Message


class InjectDishkaMiddleware(BaseMiddleware[Message]):
    def __init__(self, event: Message, view: ABCView | None, container: AsyncContainer) -> None:
        super().__init__(event, view)
        self._container = container
        self._event = event

    @override
    async def pre(self) -> None:
        self.send({"container": self._container})
