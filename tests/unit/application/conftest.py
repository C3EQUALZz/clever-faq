from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from clever_faq.application.common.ports.document.document_storage import DocumentStorage
from clever_faq.application.common.ports.scheduler.task_scheduler import TaskScheduler
from clever_faq.application.common.ports.transaction_manager import TransactionManager
from clever_faq.domain.document.ports.document_id_generator import DocumentIDGenerator


@pytest.fixture
def fake_transaction() -> TransactionManager:
    fake = Mock()
    fake.commit = AsyncMock()
    fake.flush = AsyncMock()
    return cast("TransactionManager", fake)


@pytest.fixture
def fake_document_storage() -> DocumentStorage:
    fake = Mock()
    fake.add = AsyncMock()
    fake.read_by_id = AsyncMock(return_value=None)
    return cast("DocumentStorage", fake)


@pytest.fixture
def fake_task_scheduler() -> TaskScheduler:
    fake = Mock()
    fake.schedule = AsyncMock()
    fake.make_task_id = Mock()
    fake.read_task_info = AsyncMock(return_value=None)
    return cast("TaskScheduler", fake)


@pytest.fixture
def fake_document_id_generator() -> DocumentIDGenerator:
    fake = Mock()
    return cast("DocumentIDGenerator", fake)
