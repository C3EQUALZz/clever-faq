import uuid

import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.asyncio(loop_scope="session")
async def test_create_document_success(client: AsyncClient) -> None:
    file_content = b"Sample document content"
    filename = f"doc_{uuid.uuid4().hex[:8]}.txt"

    response = await client.post(
        "/v1/documents/",
        files={
            "image": (filename, file_content, "text/plain"),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert "document_id" in data
    assert "task_id" in data
    assert isinstance(data["document_id"], str)
    assert isinstance(data["task_id"], str)
