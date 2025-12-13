import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, final

from clever_faq.application.common.ports.event_bus import EventBus
from clever_faq.application.common.ports.transaction_manager import TransactionManager
from clever_faq.application.common.ports.user.user_command_gateway import UserCommandGateway
from clever_faq.application.common.services.current_user_service import CurrentUserService
from clever_faq.application.common.views.user import CreateUserView
from clever_faq.domain.user.services.access_service import AccessService
from clever_faq.domain.user.services.authorization.permission import CanManageRole, RoleManagementContext
from clever_faq.domain.user.services.user_service import UserService
from clever_faq.domain.user.values.user_name import Username
from clever_faq.domain.user.values.user_role import UserRole

if TYPE_CHECKING:
    from clever_faq.domain.user.entities.user import User

logger: Final[logging.Logger] = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserCommand:
    name: str
    role: UserRole = UserRole.USER


@final
class CreateUserCommandHandler:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        event_bus: EventBus,
        current_user_service: CurrentUserService,
        access_service: AccessService,
    ) -> None:
        self._transaction_manager: Final[TransactionManager] = transaction_manager
        self._user_command_gateway: Final[UserCommandGateway] = user_command_gateway
        self._user_service: Final[UserService] = user_service
        self._event_bus: Final[EventBus] = event_bus
        self._current_user_service: Final[CurrentUserService] = current_user_service
        self._access_service: Final[AccessService] = access_service

    async def __call__(self, data: CreateUserCommand) -> CreateUserView:
        logger.info(
            "Create user: started. Username: '%s'.",
            data.name,
        )

        current_user: User = await self._current_user_service.get_current_user()

        self._access_service.authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=data.role,
            ),
        )

        new_user: User = self._user_service.create(
            name=Username(data.name),
            role=data.role,
        )

        await self._user_command_gateway.add(new_user)
        await self._transaction_manager.flush()
        await self._event_bus.publish(self._user_service.pull_events())
        await self._transaction_manager.commit()

        logger.info("Create user: done. Username: '%s'.", new_user.name)

        return CreateUserView(
            user_id=new_user.id,
        )
