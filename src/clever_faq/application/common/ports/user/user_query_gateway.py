from abc import abstractmethod
from typing import Protocol

from clever_faq.application.common.query_params.user_filters import UserListParams
from clever_faq.domain.user.entities.user import User
from clever_faq.domain.user.values.user_id import UserID


class UserQueryGateway(Protocol):
    @abstractmethod
    async def read_user_by_id(self, user_id: UserID) -> User | None: ...

    @abstractmethod
    async def read_all_users(self, user_list_params: UserListParams) -> list[User] | None: ...
