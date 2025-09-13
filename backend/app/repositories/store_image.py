from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.store_image import StoreImage
from repositories.base import BaseRepository


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
            
            # 트랜잭션 커밋
            await self.session.commit()
            
            # 생성된 이미지들 새로고침
            for image in created_images:
                await self.session.refresh(image)
            
            return created_images
            
        except Exception as e:
            await self.session.rollback()
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
        
        await self.session.commit()
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
    
    async def reorder_images(self, store_id: str, image_ids: List[str]) -> bool:
        """이미지 순서 재정렬 (대표 이미지 제외)"""
        # 가게의 모든 이미지 확인
        store_images = await self.get_by_store_id(store_id)
        store_image_map = {img.image_id: img for img in store_images}
        
        # 대표 이미지 확인
        main_image = next((img for img in store_images if img.is_main), None)
        if not main_image:
            raise ValueError("대표 이미지가 없습니다.")
        
        # 전달받은 image_ids에 대표 이미지가 포함되어 있으면 제거
        if main_image.image_id in image_ids:
            image_ids = [id for id in image_ids if id != main_image.image_id]
        
        # 전달받은 image_ids가 모두 해당 가게의 이미지인지 확인
        if not all(img_id in store_image_map for img_id in image_ids):
            return False
        
        # 한 번의 트랜잭션으로 모든 순서 업데이트
        try:
            # 대표 이미지는 항상 최상위
            main_image.display_order = 0
            
            # 나머지 이미지들의 display_order 업데이트
            for order, image_id in enumerate(image_ids, start=1):
                image = store_image_map[image_id]
                image.display_order = order
            
            # 변경사항을 한 번에 커밋
            await self.session.flush()
            await self.session.commit()
            
            return True
        except Exception:
            await self.session.rollback()
            return False