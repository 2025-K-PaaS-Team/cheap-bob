from typing import BinaryIO, List, Optional, Tuple

from app.domain.seller.service.exception import (
    StoreImageDuplicateError,
    StoreImageMainDeleteError,
    StoreImageNotFoundError,
    StoreNotFoundError,
)
from app.domain.seller.schema.image import (
    ImageUploadResponse,
    StoreImagesUploadResponse,
)
from app.domain.seller.repository.store_image import StoreImageRepository
from app.domain.seller.repository.store import StoreRepository
from app.database.session import UnitOfWork, transactional
from app.core.object_storage import object_storage


class SellerStoreImageService:
    """가게 이미지 업로드/조회/삭제/대표 변경.

    S3 (object_storage) 와 DB 양쪽을 다룬다. 트랜잭션은 RDB 만 보장 — S3 업로드 실패 시
    rollback 되지 않으므로 호출 순서를 (S3 → DB) 로 유지해 orphan row 를 피한다.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    async def _assert_owner(self, store_id: str, seller_email: str) -> None:
        """caller 의 @transactional 안에서만 호출 — self._session 이 설정돼 있어야 함."""
        store = await StoreRepository(self._session).get_by_store_id(store_id)
        if store is None:
            raise StoreNotFoundError("가게를 찾을 수 없습니다.")
        if store.seller_email != seller_email:
            raise StoreImageNotFoundError("권한이 없습니다.")


    @transactional
    async def init_images(
        self,
        *,
        store_id: str,
        seller_email: str,
        files: List[Tuple[BinaryIO, str, str]],
    ) -> StoreImagesUploadResponse:
        """첫 등록 — 첫 번째 파일이 대표 이미지."""
        await self._assert_owner(store_id, seller_email)
        repo = StoreImageRepository(self._session)

        if await repo.get_by_store_id(store_id):
            raise StoreImageDuplicateError("이미 등록된 이미지가 있습니다.")

        uploaded = await object_storage.upload_multiple_files(
            files=files, prefix=f"stores/{store_id}/images",
        )
        if not uploaded:
            raise StoreImageNotFoundError("업로드가 처리되지 않았습니다.")

        main_key, _ = uploaded[0]
        others = [key for key, _ in uploaded[1:]]
        created = await repo.create_initial_images(
            store_id=store_id, main_image_id=main_key, other_image_ids=others,
        )

        responses = [
            ImageUploadResponse(
                image_id=img.image_id,
                image_url=url,
                is_main=img.is_main,
                display_order=img.display_order,
            )
            for img, (_, url) in zip(created, uploaded)
        ]
        return StoreImagesUploadResponse(
            store_id=store_id, images=responses, total=len(responses),
        )


    @transactional
    async def add_images(
        self,
        *,
        store_id: str,
        seller_email: str,
        files: List[Tuple[BinaryIO, str, str]],
    ) -> StoreImagesUploadResponse:
        await self._assert_owner(store_id, seller_email)
        repo = StoreImageRepository(self._session)

        existing = await repo.get_by_store_id(store_id)
        uploaded = await object_storage.upload_multiple_files(
            files=files, prefix=f"stores/{store_id}/images",
        )
        if not uploaded:
            raise StoreImageNotFoundError("이미지 업로드에 실패했습니다.")

        max_order = max(
            (img.display_order for img in existing), default=0,
        )
        for idx, (key, _) in enumerate(uploaded):
            await repo.create_image(
                store_id=store_id,
                image_id=key,
                display_order=max_order + idx + 1,
            )

        all_images = await repo.get_by_store_id(store_id)
        responses = [
            ImageUploadResponse(
                image_id=img.image_id,
                image_url=object_storage.get_file_url(img.image_id),
                is_main=img.is_main,
                display_order=img.display_order,
            )
            for img in all_images
        ]
        return StoreImagesUploadResponse(
            store_id=store_id, images=responses, total=len(responses),
        )


    @transactional
    async def get_main_image_urls(
        self, store_ids: List[str],
    ) -> dict[str, Optional[str]]:
        """여러 가게의 대표 이미지 URL 매핑. order 도메인의 customer 주문 히스토리에서 사용."""
        return await StoreImageRepository(
            self._session,
        ).get_main_images_for_stores(store_ids)


    @transactional
    async def list_images(self, store_id: str) -> List[ImageUploadResponse]:
        images = await StoreImageRepository(self._session).get_by_store_id(store_id)
        return [
            ImageUploadResponse(
                image_id=img.image_id,
                image_url=object_storage.get_file_url(img.image_id),
                is_main=img.is_main,
                display_order=img.display_order,
            )
            for img in images
        ]


    @transactional
    async def delete_image(
        self, *, store_id: str, seller_email: str, image_id: str,
    ) -> bool:
        await self._assert_owner(store_id, seller_email)
        repo = StoreImageRepository(self._session)

        image = await repo.get_by_pk(image_id)
        if image is None or image.store_id != store_id:
            raise StoreImageNotFoundError("이미지를 찾을 수 없습니다.")
        if image.is_main:
            raise StoreImageMainDeleteError("대표 이미지는 삭제할 수 없습니다.")

        await object_storage.delete_file(image_id)
        return await repo.delete_image(image_id)


    @transactional
    async def change_main_image(
        self, *, store_id: str, seller_email: str, new_main_image_id: str,
    ) -> ImageUploadResponse:
        await self._assert_owner(store_id, seller_email)
        repo = StoreImageRepository(self._session)

        image = await repo.get_by_pk(new_main_image_id)
        if image is None or image.store_id != store_id:
            raise StoreImageNotFoundError("이미지를 찾을 수 없습니다.")

        updated = await repo.set_as_main(new_main_image_id)
        return ImageUploadResponse(
            image_id=updated.image_id,
            image_url=object_storage.get_file_url(updated.image_id),
            is_main=updated.is_main,
            display_order=updated.display_order,
        )
