from typing import List, BinaryIO, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.store import StoreRepository
from repositories.store_image import StoreImageRepository
from core.object_storage import object_storage
from core.exceptions import HTTPValueError
from schemas.image import ImageUploadResponse, StoreImagesUploadResponse
from database.models.store_image import StoreImage


class ImageService:
    """이미지 업로드 관련 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.store_repo = StoreRepository(session)
        self.store_image_repo = StoreImageRepository(session)
    
    async def init_store_images(
        self,
        store_id: str,
        seller_email: str,
        files: List[Tuple[BinaryIO, str, str]]
    ) -> StoreImagesUploadResponse:
        """
        최초 가게 이미지 업로드
        첫 번째 이미지를 대표 이미지로 설정
        
        Args:
            store_id: 가게 ID
            seller_email: 판매자 이메일
            files: [(파일 객체, 파일명, content_type)] 리스트
        
        Returns:
            StoreImagesUploadResponse
        """
        # 가게 소유권 확인
        store = await self.store_repo.get_by_store_id(store_id)
        if not store:
            raise HTTPValueError(
                detail="가게를 찾을 수 없습니다.",
                status_code=404
            )
        
        if store.seller_email != seller_email:
            raise HTTPValueError(
                detail="이 가게의 이미지를 업로드할 권한이 없습니다.",
                status_code=401
            )

        
        # 기존 이미지가 있는지 확인
        existing_images = await self.store_image_repo.get_by_store_id(store_id)
        if existing_images:
            raise HTTPValueError(
                detail="이미 등록된 이미지가 있습니다. 추가 업로드를 사용하세요.",
                status_code=409
            )
        
        # S3에 이미지 업로드
        uploaded_files = await object_storage.upload_multiple_files(
            files=files,
            prefix=f"stores/{store_id}/images"
        )
        
        if not uploaded_files:
            raise Exception("업로드가 처리 되지 않았습니다.")
        
        # 첫 번째 이미지를 대표 이미지로 설정
        main_image_key, _ = uploaded_files[0]
        other_image_keys = [key for key, _ in uploaded_files[1:]]
        
        # DB에 이미지 정보 저장
        created_images = await self.store_image_repo.create_initial_images(
            store_id=store_id,
            main_image_id=main_image_key,
            other_image_ids=other_image_keys
        )
        
        # 응답 생성
        image_responses = []
        for idx, (image, (key, url)) in enumerate(zip(created_images, uploaded_files)):
            image_responses.append(
                ImageUploadResponse(
                    image_id=image.image_id,
                    image_url=url,
                    is_main=image.is_main,
                    display_order=image.display_order
                )
            )
        
        return StoreImagesUploadResponse(
            store_id=store_id,
            images=image_responses,
            total=len(image_responses)
        )
    
    async def add_store_images(
        self,
        store_id: str,
        seller_email: str,
        files: List[Tuple[BinaryIO, str, str]]
    ) -> StoreImagesUploadResponse:
        """
        가게 이미지 추가 업로드
        
        Args:
            store_id: 가게 ID
            seller_email: 판매자 이메일
            files: [(파일 객체, 파일명, content_type)] 리스트
        
        Returns:
            StoreImagesUploadResponse
        """
        # 가게 소유권 확인
        store = await self.store_repo.get_by_store_id(store_id)
        if not store:
            raise HTTPValueError(
                detail="가게를 찾을 수 없습니다.",
                status_code=404
            )
        
        if store.seller_email != seller_email:
            raise HTTPValueError(
                detail="이 가게의 이미지를 업로드할 권한이 없습니다.",
                status_code=401
            )
        
        # 기존 이미지 개수 확인
        existing_images = await self.store_image_repo.get_by_store_id(store_id)
        
        # S3에 이미지 업로드
        uploaded_files = await object_storage.upload_multiple_files(
            files=files,
            prefix=f"stores/{store_id}/images"
        )
        
        if not uploaded_files:
            raise Exception("이미지 업로드에 실패했습니다.")
        
        # 기존 이미지의 최대 display_order 확인
        max_order = max(img.display_order for img in existing_images) if existing_images else 0
        
        # DB에 이미지 정보 저장
        created_images = []
        for idx, (key, url) in enumerate(uploaded_files):
            image = await self.store_image_repo.create_image(
                store_id=store_id,
                image_id=key,
                display_order=max_order + idx + 1
            )
            created_images.append(image)
        
        # 전체 이미지 목록 조회
        all_images = await self.store_image_repo.get_by_store_id(store_id)
        
        # 응답 생성
        image_responses = []
        for image in all_images:
            image_url = object_storage.get_file_url(image.image_id)
            image_responses.append(
                ImageUploadResponse(
                    image_id=image.image_id,
                    image_url=image_url,
                    is_main=image.is_main,
                    display_order=image.display_order
                )
            )
        
        return StoreImagesUploadResponse(
            store_id=store_id,
            images=image_responses,
            total=len(image_responses)
        )
    
    async def get_store_images(
        self,
        store_id: str
    ) -> List[ImageUploadResponse]:
        """
        가게 이미지 목록 조회
        
        Args:
            store_id: 가게 ID
        
        Returns:
            이미지 목록
        """
        images = await self.store_image_repo.get_by_store_id(store_id)
        
        image_responses = []
        for image in images:
            image_url = object_storage.get_file_url(image.image_id)
            image_responses.append(
                ImageUploadResponse(
                    image_id=image.image_id,
                    image_url=image_url,
                    is_main=image.is_main,
                    display_order=image.display_order
                )
            )
        
        return image_responses
    
    async def delete_store_image(
        self,
        store_id: str,
        seller_email: str,
        image_id: str
    ) -> bool:
        """
        가게 이미지 삭제
        
        Args:
            store_id: 가게 ID
            seller_email: 판매자 이메일
            image_id: 삭제할 이미지 ID
        
        Returns:
            성공 여부
        """
        # 가게 소유권 확인
        store = await self.store_repo.get_by_store_id(store_id)
        if not store:
            raise HTTPValueError(
                detail="가게를 찾을 수 없습니다.",
                status_code=404
            )
        
        if store.seller_email != seller_email:
            raise HTTPValueError(
                detail="이 가게의 이미지를 삭제할 권한이 없습니다.",
                status_code=403
            )
        
        # 이미지 정보 조회
        image = await self.store_image_repo.get_by_pk(image_id)
        if not image or image.store_id != store_id:
            raise HTTPValueError(
                detail="이미지를 찾을 수 없습니다.",
                status_code=404
            )
        
        if image.is_main:
            raise HTTPValueError(
                detail="대표 이미지는 삭제할 수 없습니다.",
                status_code=409
            )
        
        # S3에서 파일 삭제
        await object_storage.delete_file(image_id)
        
        # DB에서 이미지 정보 삭제
        return await self.store_image_repo.delete_image(image_id)
    
    async def change_main_image(
        self,
        store_id: str,
        seller_email: str,
        new_main_image_id: str
    ) -> ImageUploadResponse:
        """
        대표 이미지 변경
        
        Args:
            store_id: 가게 ID
            seller_email: 판매자 이메일
            new_main_image_id: 새로운 대표 이미지 ID
        
        Returns:
            변경된 대표 이미지 정보
        """
        # 가게 소유권 확인
        store = await self.store_repo.get_by_store_id(store_id)
        if not store:
            raise HTTPValueError(
                detail="가게를 찾을 수 없습니다.",
                status_code=404
            )

        
        if store.seller_email != seller_email:
            raise HTTPValueError(
                detail="이 가게의 이미지를 변경할 권한이 없습니다.",
                status_code=403
            )
        
        # 이미지 정보 조회
        image = await self.store_image_repo.get_by_pk(new_main_image_id)
        if not image or image.store_id != store_id:
            raise HTTPValueError(
                detail="이미지를 찾을 수 없습니다.",
                status_code=404
            )
        
        # 대표 이미지 변경
        updated_image = await self.store_image_repo.set_as_main(new_main_image_id)
        
        image_url = object_storage.get_file_url(updated_image.image_id)
        
        return ImageUploadResponse(
            image_id=updated_image.image_id,
            image_url=image_url,
            is_main=updated_image.is_main,
            display_order=updated_image.display_order
        )