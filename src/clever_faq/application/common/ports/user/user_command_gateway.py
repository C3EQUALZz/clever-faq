from abc import abstractmethod
from typing import Protocol

from clever_faq.domain.user.entities.user import User
from clever_faq.domain.user.values.user_id import UserID


class UserCommandGateway(Protocol):
    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def read_by_id(self, user_id: UserID) -> User | None: ...

    @abstractmethod
    async def delete_by_id(self, user_id: UserID) -> None: ...

    @abstractmethod
    async def update(self, user: User) -> None: ...
