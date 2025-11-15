import io
import logging
from datetime import UTC, datetime
from typing import Any, Final, override

from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError, EndpointConnectionError
from tenacity import retry, stop_after_attempt, wait_exponential

from clever_faq.application.common.ports.document.document_storage import DocumentDTO, DocumentStorage
from clever_faq.domain.document.values.document_id import DocumentID
from clever_faq.domain.document.values.document_name import DocumentName
from clever_faq.domain.document.values.document_type import DocumentType
from clever_faq.infrastructure.errors.persistence import FileStorageError
from clever_faq.infrastructure.persistence.adapters.constants import DOWNLOAD_FILE_FAILED, UPLOAD_FILE_FAILED
from clever_faq.setup.config.s3 import S3Config

logger: Final[logging.Logger] = logging.getLogger(__name__)


class AiobotocoreDocumentStorage(DocumentStorage):
    def __init__(self, client: AioBaseClient, s3_config: S3Config) -> None:
        self._client: Final[AioBaseClient] = client
        self._bucket_name: Final[str] = s3_config.documents_bucket_name

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    @override
    async def add(self, document: DocumentDTO) -> None:
        try:
            s3_key: str = f"documents/{document.document_id!s}"
            logger.debug("Build s3 key for storage: %s", s3_key)

            await self._client.upload_fileobj(
                io.BytesIO(document.document_content),
                self._bucket_name,
                s3_key,
                ExtraArgs={
                    "Metadata": {
                        "original_filename": document.document_name.value,
                        "document_type": document.document_type.value,
                        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "updated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    },
                    "ContentType": "application/octet-stream",
                },
            )

        except EndpointConnectionError as e:
            logger.exception(UPLOAD_FILE_FAILED)
            raise FileStorageError(UPLOAD_FILE_FAILED) from e

        except ClientError as e:
            logger.exception(UPLOAD_FILE_FAILED)
            raise FileStorageError(UPLOAD_FILE_FAILED) from e

        except Exception as e:
            logger.exception(UPLOAD_FILE_FAILED)
            raise FileStorageError(UPLOAD_FILE_FAILED) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    @override
    async def read_by_id(self, document_id: DocumentID) -> DocumentDTO | None:
        s3_key: str = f"documents/{document_id!s}"
        logger.debug("Build s3 key for storage: %s", s3_key)

        try:
            response = await self._client.get_object(Bucket=self._bucket_name, Key=s3_key)
            metadata: dict[str, Any] = response.get("Metadata", {})
            original_filename: str = metadata.get("original_filename", s3_key.split("/")[-1])

            file_data = await response["Body"].read()

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning("File not found in S3: %s", s3_key)
                return None
            logger.exception(DOWNLOAD_FILE_FAILED)
            raise FileStorageError(DOWNLOAD_FILE_FAILED) from e
        except EndpointConnectionError as e:
            logger.exception(DOWNLOAD_FILE_FAILED)
            raise FileStorageError(DOWNLOAD_FILE_FAILED) from e
        except Exception as e:
            logger.exception(DOWNLOAD_FILE_FAILED)
            raise FileStorageError(DOWNLOAD_FILE_FAILED) from e
        else:
            return DocumentDTO(
                document_id=document_id,
                document_name=DocumentName(original_filename),
                document_content=file_data,
                document_type=DocumentType(metadata["document_type"]),
            )
