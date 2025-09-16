import boto3
import uuid
from typing import BinaryIO, Optional, List, Tuple
from datetime import datetime
from botocore.exceptions import ClientError
from botocore.config import Config
from loguru import logger

from config.settings import settings


class ObjectStorage:
    """AWS S3 객체 스토리지 관리 클래스"""
    
    def __init__(self):
        """S3 클라이언트 초기화"""
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        
        # 재시도 설정
        config = Config(
            region_name=settings.AWS_REGION,
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )
        
        # S3 클라이언트 생성
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=config
        )
    
    def _generate_file_key(self, extension: str, prefix: str) -> str:
        """파일 키 생성"""
        unique_id = str(uuid.uuid4())
        
        return f"{prefix}/{unique_id}.{extension}"
    
    async def upload_file(
        self, 
        file: BinaryIO, 
        file_name: str,
        prefix: str,
        content_type: str
    ) -> Tuple[str, str]:
        """
        파일을 S3에 업로드
        
        Args:
            file: 업로드할 파일 객체
            file_name: 원본 파일명
            prefix: S3 키 프리픽스에 사용할 가게 이름
            content_type: 파일의 Content-Type - JPG, JPEG, PNG, WEBP
        
        Returns:
            (file_key, file_url) 튜플
        """
        try:
            # 파일 키 생성
            extension = file_name.split('.')[-1] if '.' in file_name else ''
            file_key = self._generate_file_key(extension, prefix)
            
            # S3에 업로드
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # 퍼블릭 읽기 권한 부여
                }
            )
            
            # URL 생성
            file_url = f"{settings.AWS_S3_ENDPOINT_URL}/{self.bucket_name}/{file_key}"

            
            return file_key, file_url
            
        except ClientError as e:
            raise Exception(f"파일 업로드 실패: {str(e)}")
    
    async def upload_multiple_files(
        self, 
        files: List[Tuple[BinaryIO, str, str]],
        prefix: str
    ) -> List[Tuple[str, str]]:
        """
        여러 파일을 S3에 업로드
        
        Args:
            files: [(파일 객체, 파일명, content_type)] 리스트
            prefix: S3 키 프리픽스
        
        Returns:
            [(file_key, file_url)] 리스트
        """
        results = []
        
        for file, file_name, content_type in files:
            try:
                file_key, file_url = await self.upload_file(
                    file=file,
                    file_name=file_name,
                    prefix=prefix,
                    content_type=content_type
                )
                results.append((file_key, file_url))
            except Exception as e:
                logger.error(f"파일 업로드 실패 ({file_key}): {str(e)}")
                raise e
        
        return results
    
    def get_file_url(self, file_key: str) -> str:
        """파일 키로 URL 생성"""
        return f"{settings.AWS_S3_ENDPOINT_URL}/{self.bucket_name}/{file_key}"

    async def delete_file(self, file_key: str) -> bool:
        """
        S3에서 파일 삭제
        
        Args:
            file_key: 삭제할 파일의 키
        
        Returns:
            성공 여부
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            logger.error(f"파일 삭제 실패 ({file_key}): {str(e)}")
            return False


# 싱글톤 인스턴스
object_storage = ObjectStorage()