"""CustomerFavoriteService 의 실 DB 흐름.

비즈니스 시나리오:
  1) 가게 존재 확인은 seller 도메인 service 에 위임 (strict service-to-service)
  2) 정상 add → DB 에 row 생성
  3) 같은 (customer, store) 재추가 → ``FavoriteAlreadyExistsError``
  4) 존재하지 않는 store → ``StoreNotFoundError``
  5) remove 후 row 없음 / 비존재 remove 시 ``FavoriteNotFoundError``
"""
import pytest
import pytest_asyncio

from app.domain.customer.service.customer_favorite import CustomerFavoriteService
from app.domain.customer.service.exception import (
    FavoriteAlreadyExistsError,
    FavoriteNotFoundError,
    StoreNotFoundError,
)
from app.domain.seller.service.seller_store_read import SellerStoreReadService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def customer_favorite_service(uow):
    return CustomerFavoriteService(
        uow=uow,
        seller_store_read_service=SellerStoreReadService(uow=uow),
    )


@pytest_asyncio.fixture
async def seed_store(session_factory, seed_seller):
    """Store row 만 심고 store_id 를 돌려준다 (favorite FK 충족)."""
    from app.domain.seller.model.store import Store

    counter = {"value": 0}

    async def _seed() -> str:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_fav_{idx:03d}"
            session.add(Store(
                store_id=store_id,
                store_name=f"즐겨가게_{idx}",
                seller_email=seller_email,
            ))
            await session.commit()
        return store_id

    return _seed


class TestAdd:

    async def test_creates_row(
        self, customer_favorite_service, seed_customer, seed_store, session_factory,
    ):
        [email] = await seed_customer(1)
        store_id = await seed_store()

        await customer_favorite_service.add(customer_email=email, store_id=store_id)

        from app.domain.customer.model.customer_favorite import CustomerFavorite
        from sqlalchemy import select
        async with session_factory() as session:
            result = await session.execute(
                select(CustomerFavorite).where(
                    CustomerFavorite.customer_email == email,
                    CustomerFavorite.store_id == store_id,
                ),
            )
            assert result.scalar_one_or_none() is not None


    async def test_duplicate_raises(
        self, customer_favorite_service, seed_customer, seed_store,
    ):
        [email] = await seed_customer(1)
        store_id = await seed_store()

        await customer_favorite_service.add(customer_email=email, store_id=store_id)
        with pytest.raises(FavoriteAlreadyExistsError):
            await customer_favorite_service.add(
                customer_email=email, store_id=store_id,
            )


    async def test_unknown_store_raises(
        self, customer_favorite_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        with pytest.raises(StoreNotFoundError):
            await customer_favorite_service.add(
                customer_email=email, store_id="STR_unknown",
            )


class TestRemove:

    async def test_removes_existing_row(
        self, customer_favorite_service, seed_customer, seed_store, session_factory,
    ):
        [email] = await seed_customer(1)
        store_id = await seed_store()
        await customer_favorite_service.add(customer_email=email, store_id=store_id)

        await customer_favorite_service.remove(customer_email=email, store_id=store_id)

        from app.domain.customer.model.customer_favorite import CustomerFavorite
        from sqlalchemy import select
        async with session_factory() as session:
            result = await session.execute(
                select(CustomerFavorite).where(
                    CustomerFavorite.customer_email == email,
                    CustomerFavorite.store_id == store_id,
                ),
            )
            assert result.scalar_one_or_none() is None


    async def test_missing_row_raises(
        self, customer_favorite_service, seed_customer, seed_store,
    ):
        [email] = await seed_customer(1)
        store_id = await seed_store()

        with pytest.raises(FavoriteNotFoundError):
            await customer_favorite_service.remove(
                customer_email=email, store_id=store_id,
            )
