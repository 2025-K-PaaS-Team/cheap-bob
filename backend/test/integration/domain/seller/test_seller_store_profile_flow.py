"""SellerStoreProfileService 의 실 DB 흐름.

비즈니스 시나리오:
  1) name / introduction / phone 각각이 DB 에 반영
  2) 미존재 store 에 대한 update 는 ``StoreNotFoundError``
"""
import pytest
import pytest_asyncio

from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.seller.service.seller_store_profile import SellerStoreProfileService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def seller_store_profile_service(uow):
    return SellerStoreProfileService(uow=uow)


@pytest_asyncio.fixture
async def seed_store(session_factory, seed_seller):
    from app.domain.seller.model.store import Store

    counter = {"value": 0}

    async def _seed() -> str:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_prof_{idx:03d}"
            session.add(Store(
                store_id=store_id,
                store_name="이전이름",
                seller_email=seller_email,
                store_introduction="이전소개",
                store_phone="02-0000-0000",
            ))
            await session.commit()
        return store_id

    return _seed


class TestUpdateFields:

    async def test_update_name(
        self, seller_store_profile_service, seed_store, session_factory,
    ):
        store_id = await seed_store()
        await seller_store_profile_service.update_name(store_id, "새이름")

        from app.domain.seller.model.store import Store
        async with session_factory() as session:
            store = await session.get(Store, store_id)
            assert store.store_name == "새이름"


    async def test_update_introduction(
        self, seller_store_profile_service, seed_store, session_factory,
    ):
        store_id = await seed_store()
        await seller_store_profile_service.update_introduction(store_id, "신규소개")

        from app.domain.seller.model.store import Store
        async with session_factory() as session:
            store = await session.get(Store, store_id)
            assert store.store_introduction == "신규소개"


    async def test_update_phone(
        self, seller_store_profile_service, seed_store, session_factory,
    ):
        store_id = await seed_store()
        await seller_store_profile_service.update_phone(store_id, "02-9999-9999")

        from app.domain.seller.model.store import Store
        async with session_factory() as session:
            store = await session.get(Store, store_id)
            assert store.store_phone == "02-9999-9999"


class TestMissingStore:

    async def test_update_name_raises(self, seller_store_profile_service):
        with pytest.raises(StoreNotFoundError):
            await seller_store_profile_service.update_name("STR_unknown", "x")
