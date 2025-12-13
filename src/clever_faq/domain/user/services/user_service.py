from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final

from clever_faq.domain.common.services.base import DomainService
from clever_faq.domain.document.entities.document import Document
from clever_faq.domain.user.entities.user import User
from clever_faq.domain.user.errors import RoleAssignmentNotPermittedError
from clever_faq.domain.user.events import (
    UserAddedDocumentEvent,
    UserChangedNameEvent,
    UserCreatedEvent,
)
from clever_faq.domain.user.ports.user_id_generator import UserIdGenerator
from clever_faq.domain.user.values.user_name import Username
from clever_faq.domain.user.values.user_role import UserRole

if TYPE_CHECKING:
    from clever_faq.domain.user.values.user_id import UserID


class UserService(DomainService):
    """
    Domain service for users.
    """

    def __init__(
        self,
        user_id_generator: UserIdGenerator,
    ) -> None:
        super().__init__()
        self._user_id_generator: Final[UserIdGenerator] = user_id_generator

    def create(
        self,
        name: Username,
        role: UserRole = UserRole.USER,
    ) -> User:
        """
        Fabric method that creates a new user.

        :param name: Username of the user.
        :param role: Role of the user.
        :return: User entity if all checks passed.

        NOTE:
            - produces event that user was created.
        """
        if not role.is_assignable:
            msg: str = f"Assignment of role: {role} not permitted."
            raise RoleAssignmentNotPermittedError(msg)

        new_user_id: UserID = self._user_id_generator()

        new_user: User = User(
            id=new_user_id,
            name=name,
            role=role,
        )

        new_event: UserCreatedEvent = UserCreatedEvent(
            user_id=new_user_id,
            name=str(new_user.name),
            role=new_user.role,
        )

        self._record_event(new_event)

        return new_user

    def change_name(self, user: User, new_user_name: Username) -> None:
        """
        Method that changes the name of the given user.

        :param user: Existing user entity in a database.
        :param new_user_name: New username for entity.
        :return: Nothing.

        Note:
            - produces event that user changed the name.
        """
        old_user_name: Username = user.name
        user.name = new_user_name
        user.updated_at = datetime.now(UTC)

        new_event: UserChangedNameEvent = UserChangedNameEvent(
            user_id=user.id,
            old_name=str(old_user_name),
            new_name=str(new_user_name),
            role=str(user.role),
        )

        self._record_event(new_event)

    def add_document(self, user: User, document: Document) -> None:
        user.documents.append(document.id)
        user.updated_at = datetime.now(UTC)

        new_event: UserAddedDocumentEvent = UserAddedDocumentEvent(
            user_id=user.id,
            document_id=document.id,
        )

        self._record_event(new_event)
