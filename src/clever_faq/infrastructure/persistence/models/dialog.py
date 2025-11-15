from typing import Final

import sqlalchemy as sa
from sqlalchemy.orm import composite

from clever_faq.domain.dialog.entities.dialog import Dialog
from clever_faq.domain.dialog.values.message import Message
from clever_faq.domain.dialog.values.tokens import Tokens
from clever_faq.infrastructure.persistence.models.base import mapper_registry

dialogs_table: Final[sa.Table] = sa.Table(
    "dialogs",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("question", sa.Text, nullable=False),
    sa.Column("answer", sa.Text, nullable=False),
    sa.Column("tokens", sa.Integer, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    ),
    sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)


def map_dialog_table() -> None:
    mapper_registry.map_imperatively(
        Dialog,
        dialogs_table,
        properties={
            "id": dialogs_table.c.id,
            "question": composite(Message, dialogs_table.c.question),
            "answer": composite(Message, dialogs_table.c.answer),
            "tokens": composite(Tokens, dialogs_table.c.tokens),
            "created_at": dialogs_table.c.created_at,
            "updated_at": dialogs_table.c.updated_at,
        },
        column_prefix="_",
    )
