"""AWS S3 객체 스토리지 — boto3 동기 클라이언트를 스레드풀로 위임."""
import uuid
from typing import BinaryIO, List, Tuple
from loguru import logger
from botocore.exceptions import ClientError
from botocore.config import Config
import boto3
import asyncio

from app.config.setting import settings


class ObjectStorage:
    """boto3 동기 클라이언트를 ``asyncio.to_thread`` 로 위임해 이벤트 루프 블로킹을 피한다."""

    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET_NAME

        config = Config(
            region_name=settings.AWS_REGION,
            retries={"max_attempts": 3, "mode": "standard"},
        )
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=config,
        )


    def _generate_file_key(self, extension: str, prefix: str) -> str:
        unique_id = str(uuid.uuid4())
        return f"{prefix}/{unique_id}.{extension}"


    async def upload_file(
        self,
        file: BinaryIO,
        file_name: str,
        prefix: str,
        content_type: str,
    ) -> Tuple[str, str]:
        """단일 파일 업로드 — (file_key, file_url) 반환. 실패 시 ``ClientError`` 전파."""
        extension = file_name.split(".")[-1] if "." in file_name else ""
        file_key = self._generate_file_key(extension, prefix)

        await asyncio.to_thread(
            self.s3_client.upload_fileobj,
            file,
            self.bucket_name,
            file_key,
            ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
        )

        file_url = f"{settings.AWS_S3_ENDPOINT_URL}/{self.bucket_name}/{file_key}"
        return file_key, file_url


    async def upload_multiple_files(
        self,
        files: List[Tuple[BinaryIO, str, str]],
        prefix: str,
    ) -> List[Tuple[str, str]]:
        """여러 파일을 순차 업로드 — 부분 실패 시 ``ClientError`` 그대로 전파."""
        results: List[Tuple[str, str]] = []
        for file, file_name, content_type in files:
            results.append(await self.upload_file(
                file=file,
                file_name=file_name,
                prefix=prefix,
                content_type=content_type,
            ))
        return results


    def get_file_url(self, file_key: str) -> str:
        return f"{settings.AWS_S3_ENDPOINT_URL}/{self.bucket_name}/{file_key}"


    async def delete_file(self, file_key: str) -> bool:
        """삭제 실패는 swallow + False 반환 — caller 는 best-effort 로 호출."""
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=file_key,
            )
            return True
        except ClientError as e:
            logger.error(f"파일 삭제 실패 ({file_key}): {str(e)}")
            return False


# 싱글톤 인스턴스 — main.py / container.py 가 공유.
object_storage = ObjectStorage()
