from typing import Final, override

from sqlalchemy import Delete, Select, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from clever_faq.application.common.ports.dialog.dialog_command_gateway import DialogCommandGateway
from clever_faq.domain.dialog.entities.dialog import Dialog
from clever_faq.domain.dialog.values.dialog_id import DialogID
from clever_faq.infrastructure.errors.persistence import RepoError
from clever_faq.infrastructure.persistence.adapters.constants import DB_QUERY_FAILED


class SqlAlchemyDialogCommandGateway(DialogCommandGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    @override
    async def add(self, dialog: Dialog) -> None:
        try:
            self._session.add(dialog)
        except SQLAlchemyError as error:
            raise RepoError(DB_QUERY_FAILED) from error

    @override
    async def delete_by_id(self, dialog_id: DialogID) -> None:
        delete_stm: Delete = delete(Dialog).where(Dialog.id == dialog_id)

        try:
            await self._session.execute(delete_stm)
        except SQLAlchemyError as error:
            raise RepoError(DB_QUERY_FAILED) from error

    @override
    async def read_by_id(self, dialog_id: DialogID) -> Dialog | None:
        select_stmt: Select[tuple[Dialog]] = select(Dialog).where(Dialog.id == dialog_id)

        try:
            dialog: Dialog | None = (await self._session.execute(select_stmt)).scalar_one_or_none()
        except SQLAlchemyError as error:
            raise RepoError(DB_QUERY_FAILED) from error
        else:
            return dialog
