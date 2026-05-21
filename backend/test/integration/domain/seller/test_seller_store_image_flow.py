"""SellerStoreImageService 의 실 DB 흐름 (S3 호출 경로 제외).

비즈니스 시나리오:
  1) ``list_images`` 가 가게의 이미지를 대표 → 추가 순으로 반환
  2) ``get_main_image_urls`` 가 store_id → URL 매핑 반환
  3) ``change_main_image`` 가 현재 대표를 새 이미지로 토글

S3 와 결합한 ``init_images`` / ``add_images`` / ``delete_image`` 는 ``object_storage`` 와의
실시간 통신이 필요해 본 integration 에서는 생략한다. URL 생성 (``get_file_url``) 은 단순
문자열 조합이라 외부 호출 없이 안전.
"""
import pytest
import pytest_asyncio

from app.domain.seller.service.seller_store_image import SellerStoreImageService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def seller_store_image_service(uow):
    return SellerStoreImageService(uow=uow)


@pytest_asyncio.fixture
async def seed_store_with_images(session_factory, seed_seller):
    from app.domain.seller.model.store import Store
    from app.domain.seller.model.store_image import StoreImage

    counter = {"value": 0}

    async def _seed(*, image_count: int = 2) -> tuple[str, str, list[str]]:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_img_{idx:03d}"
            session.add(Store(
                store_id=store_id, store_name="가게", seller_email=seller_email,
            ))
            await session.flush()

            ids: list[str] = []
            for i in range(image_count):
                image_id = f"stores/{store_id}/images/{i:03d}.jpg"
                ids.append(image_id)
                session.add(StoreImage(
                    image_id=image_id,
                    store_id=store_id,
                    is_main=(i == 0),
                    display_order=i,
                ))
            await session.commit()
        return store_id, seller_email, ids

    return _seed


class TestListImages:

    async def test_returns_main_first(
        self, seller_store_image_service, seed_store_with_images,
    ):
        store_id, _, ids = await seed_store_with_images(image_count=3)

        responses = await seller_store_image_service.list_images(store_id)
        assert len(responses) == 3
        assert responses[0].is_main is True
        assert responses[0].image_id == ids[0]


class TestMainImageUrls:

    async def test_returns_url_for_each_store(
        self, seller_store_image_service, seed_store_with_images,
    ):
        s1, _, _ = await seed_store_with_images()
        s2, _, _ = await seed_store_with_images()

        urls = await seller_store_image_service.get_main_image_urls([s1, s2])
        assert urls[s1] is not None
        assert urls[s2] is not None


    async def test_unknown_store_gets_none(
        self, seller_store_image_service, seed_store_with_images,
    ):
        s1, _, _ = await seed_store_with_images()
        urls = await seller_store_image_service.get_main_image_urls(
            [s1, "STR_no"],
        )
        assert urls[s1] is not None
        assert urls["STR_no"] is None


class TestChangeMainImage:

    async def test_toggles_is_main_flag(
        self, seller_store_image_service, seed_store_with_images, session_factory,
    ):
        store_id, seller_email, ids = await seed_store_with_images(image_count=2)
        new_main = ids[1]

        response = await seller_store_image_service.change_main_image(
            store_id=store_id, seller_email=seller_email, new_main_image_id=new_main,
        )
        assert response.image_id == new_main
        assert response.is_main is True

        from app.domain.seller.model.store_image import StoreImage
        async with session_factory() as session:
            old = await session.get(StoreImage, ids[0])
            assert old.is_main is False
