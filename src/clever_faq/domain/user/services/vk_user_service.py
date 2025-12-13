from typing import Final

from clever_faq.domain.common.services.base import DomainService
from clever_faq.domain.user.entities.vk_user import VkUser
from clever_faq.domain.user.services.user_service import UserService
from clever_faq.domain.user.values.vk_first_name import VkUserFirstName
from clever_faq.domain.user.values.vk_last_name import VkUserLastName


class VkUserService(DomainService):
    def __init__(self, user_service: UserService) -> None:
        super().__init__()
        self._user_service: Final[UserService] = user_service

    def create(
        self,
        vk_user_first_name: VkUserFirstName,
        vk_user_last_name: VkUserLastName,
    ) -> VkUser:
        """
        Fabric method that creates a new user.

        :param vk_user_first_name: Username of the user.
        :param vk_user_last_name: Role of the user.
        :return: User entity if all checks passed.

        NOTE:
            - produces event that user was created.
        """
