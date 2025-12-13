import logging
from typing import TYPE_CHECKING, Final

from clever_faq.application.common.ports.identity_provider import IdentityProvider
from clever_faq.application.common.ports.user.user_command_gateway import UserCommandGateway
from clever_faq.domain.user.entities.user import User

if TYPE_CHECKING:
    from clever_faq.domain.user.values.user_id import UserID

logger: Final[logging.Logger] = logging.getLogger(__name__)


class CurrentUserService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_command_gateway: UserCommandGateway,
    ) -> None:
        self._identity_provider: Final[IdentityProvider] = identity_provider
        self._user_command_gateway: Final[UserCommandGateway] = user_command_gateway
        self._cached_current_user: User | None = None

    async def get_current_user(self) -> User:
        if self._cached_current_user is not None:
            return self._cached_current_user

        current_user_id: UserID = await self._identity_provider.get_current_user_id()
        user: User | None = await self._user_command_gateway.read_by_id(current_user_id)

        self._cached_current_user = user
        return user
