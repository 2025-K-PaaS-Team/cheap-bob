from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database.models.store_image import StoreImage
from repositories.base import BaseRepository
from core.object_storage import object_storage

class StoreImageRepository(BaseRepository[StoreImage]):
    """가게 이미지 Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(StoreImage, session)
    
    async def get_by_store_id(self, store_id: str) -> List[StoreImage]:
        """가게 ID로 이미지 목록 조회"""
        return await self.get_many(
            filters={"store_id": store_id},
            order_by=["-is_main", "display_order", "created_at"]
        )
    
    async def get_main_image(self, store_id: str) -> Optional[StoreImage]:
        """가게의 대표 이미지 조회"""
        return await self.get_one(
            store_id=store_id,
            is_main=True
        )
    
    async def create_image(
        self,
        store_id: str,
        image_id: str,
        display_order: int
    ) -> StoreImage:
        """이미지 생성"""
        
        return await self.create(
            store_id=store_id,
            image_id=image_id,
            is_main=False,
            display_order=display_order
        )
    
    async def create_initial_images(
        self,
        store_id: str,
        main_image_id: str,
        other_image_ids: List[str] = None
    ) -> List[StoreImage]:
        """최초 이미지 등록 (대표 이미지 필수)"""
        
        # 이미 대표 이미지가 있는지 체크
        existing_images = await self.get_by_store_id(store_id)
        if existing_images:
            raise ValueError("이미 등록된 이미지가 있습니다.")
        
        created_images = []
        
        try:
            # 1. 대표 이미지 생성
            main_image = await self.create(
                store_id=store_id,
                image_id=main_image_id,
                is_main=True,
                display_order=0
            )
            created_images.append(main_image)
            
            # 2. 추가 이미지들 생성 (옵션)
            if other_image_ids:
                for idx, image_id in enumerate(other_image_ids, start=1):
                    additional_image = await self.create(
                        store_id=store_id,
                        image_id=image_id,
                        is_main=False,
                        display_order=idx
                    )
                    created_images.append(additional_image)
            
            # 변경사항 플러시
            await self.session.flush()
            
            # 생성된 이미지들 새로고침
            for image in created_images:
                await self.session.refresh(image)
            
            return created_images
            
        except Exception as e:
            raise e
    
    async def set_as_main(self, image_id: str) -> Optional[StoreImage]:
        """대표 이미지 교체"""
        
        image = await self.get_by_pk(image_id)
        if not image:
            return None
        
        # 이미 대표 이미지인 경우
        if image.is_main:
            return image
        
        # 트랜잭션 내에서 처리하여 원자성 보장
        # 기존 대표 이미지 조회
        current_main = await self.get_main_image(image.store_id)
        
        if not current_main:
            raise ValueError("대표 이미지가 없습니다. create_initial_images를 사용하세요.")
        
        current_main.is_main = False
        image.is_main = True
        
        # 변경사항을 세션에 반영
        await self.session.flush()
        await self.session.refresh(image)
        
        return image
    
    async def delete_image(self, image_id: str) -> bool:
        """이미지 삭제 (대표 이미지는 삭제 불가)"""
        image = await self.get_by_pk(image_id)
        if not image:
            return False
        
        # 대표 이미지는 삭제할 수 없음
        if image.is_main:
            raise ValueError("대표 이미지는 삭제할 수 없습니다.")
        
        return await self.delete(image_id)
    
    async def get_main_images_for_stores(self, store_ids: List[str]) -> Dict[str, Optional[str]]:
        """여러 가게의 대표 이미지 URL을 한 번에 조회"""
        if not store_ids:
            return {}
        
        stmt = (
            select(StoreImage)
            .where(
                and_(
                    StoreImage.store_id.in_(store_ids),
                    StoreImage.is_main == True
                )
            )
        )
        result = await self.session.execute(stmt)
        main_images = result.scalars().all()
        
        main_image_dict = {img.store_id: object_storage.get_file_url(img.image_id) for img in main_images}
        
        return {store_id: main_image_dict.get(store_id) for store_id in store_ids}