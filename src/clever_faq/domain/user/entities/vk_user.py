from dataclasses import dataclass

from clever_faq.domain.common.entities.base_aggregate import BaseAggregateRoot
from clever_faq.domain.user.values.vk_first_name import VkUserFirstName
from clever_faq.domain.user.values.vk_id import VkID
from clever_faq.domain.user.values.vk_last_name import VkUserLastName


@dataclass(eq=False, kw_only=True)
class VkUser(BaseAggregateRoot[VkID]):
    first_name: VkUserFirstName
    last_name: VkUserLastName
