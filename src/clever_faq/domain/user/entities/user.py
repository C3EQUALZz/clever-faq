from dataclasses import dataclass, field

from clever_faq.domain.common.entities.base_entity import BaseEntity
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.user.values.user_id import UserID
from clever_faq.domain.user.values.user_name import Username
from clever_faq.domain.user.values.user_role import UserRole


@dataclass(eq=False, kw_only=True)
class User(BaseEntity[UserID]):
    """
    Aggregate which represents a user account in system.

    NOTE:
        - id is UUID type for unique
        - email must be valid type. Please check for real email before creating an account.
        - password must be hashed before creating an account. Check for hash in service.
        - role. For description check enum UserRole.
        - is_active. True if user not blocked by admin. False otherwise.
    """

    name: Username
    role: UserRole = field(default_factory=lambda: UserRole.USER)
    is_active: bool = field(default_factory=lambda: True)
    documents: list[DocumentID] = field(default_factory=list)
