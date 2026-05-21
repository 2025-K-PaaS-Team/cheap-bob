"""SellerStoreReadService 의 실 DB 흐름.

비즈니스 시나리오:
  1) ``get_with_full_info`` 가 store + address/sns/operation/products 를 한 번에 eager-load
  2) ``list_with_products`` 는 상품 있는 가게만 페이지네이션해 반환
  3) ``search_by_location`` / ``search_by_name`` 이 조건 매칭 가게를 반환
  4) ``get_by_store_ids`` 는 주어진 ID 목록의 가게만 full-info 와 함께 반환
     (customer favorite 결합은 customer 도메인 책임 — favorite 자체는 customer 통합 테스트에서 검증)

Redis 캐시를 쓰는 ``get_store_id_by_seller_email`` 은 Redis 의존성이 있어 본 통합 테스트에서는 다루지 않는다.
"""
import pytest_asyncio
import pytest
from datetime import time

from app.domain.seller.service.seller_store_read import SellerStoreReadService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def seller_store_read_service(uow):
    return SellerStoreReadService(uow=uow)


@pytest_asyncio.fixture
async def seed_full_store(session_factory, seed_seller):
    """Store + Address + Product + Operation 한 세트.

    list_with_products / search_by_location 등이 동작하려면 product 와 address join 이
    필요하므로 한 fixture 로 묶었다.
    """
    from app.domain.seller.model.store import Store
    from app.domain.seller.model.store_address import StoreAddress
    from app.domain.seller.model.store_operation_info import StoreOperationInfo
    from app.domain.seller.model.store_product_info import StoreProductInfo

    counter = {"value": 0}

    async def _seed(
        *,
        sido: str = "서울특별시",
        sigungu: str = "강남구",
        bname: str = "역삼동",
        store_name: str = "통합테스트가게",
        product_name: str = "통합테스트상품",
    ) -> tuple[str, str]:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_full_{idx:03d}"
            product_id = f"PRD_full_{idx:03d}"

            address = StoreAddress(
                sido=sido, sigungu=sigungu, bname=bname, lat="37.5", lng="127.0",
            )
            session.add(address)
            await session.flush()

            session.add(Store(
                store_id=store_id,
                store_name=store_name,
                seller_email=seller_email,
                address_id=address.address_id,
            ))
            session.add(StoreProductInfo(
                product_id=product_id,
                store_id=store_id,
                product_name=product_name,
                initial_stock=10,
                price=10000,
            ))
            session.add(StoreOperationInfo(
                store_id=store_id,
                day_of_week=0,
                open_time=time(10, 0),
                close_time=time(22, 0),
                pickup_start_time=time(11, 0),
                pickup_end_time=time(21, 0),
                is_open_enabled=True,
                is_currently_open=False,
            ))
            await session.commit()
        return store_id, product_id

    return _seed


class TestGetWithFullInfo:

    async def test_loads_all_relations(self, seller_store_read_service, seed_full_store):
        store_id, _ = await seed_full_store()

        store = await seller_store_read_service.get_with_full_info(store_id)
        assert store is not None
        assert store.address is not None
        assert len(store.products) == 1
        assert len(store.operation_info) == 1


    async def test_returns_none_when_missing(self, seller_store_read_service):
        assert await seller_store_read_service.get_with_full_info("STR_no") is None


class TestListWithProducts:

    async def test_paginates_with_is_end_flag(
        self, seller_store_read_service, seed_full_store,
    ):
        # 5개 가게를 만든다 (limit 4, offset 0 → is_end False, 다음 페이지 4 → True).
        for _ in range(5):
            await seed_full_store()

        first, is_end1 = await seller_store_read_service.list_with_products(
            offset=0, limit=4,
        )
        second, is_end2 = await seller_store_read_service.list_with_products(
            offset=4, limit=4,
        )
        assert len(first) == 4
        assert is_end1 is False
        assert len(second) == 1
        assert is_end2 is True


class TestSearch:

    async def test_search_by_location_filters_matching(
        self, seller_store_read_service, seed_full_store,
    ):
        a_id, _ = await seed_full_store(sigungu="강남구", bname="역삼동")
        b_id, _ = await seed_full_store(sigungu="강남구", bname="삼성동")

        result, _ = await seller_store_read_service.search_by_location(
            sido="서울특별시", sigungu="강남구", bname=["역삼동"],
            offset=0, limit=4,
        )
        ids = {s.store_id for s in result}
        assert a_id in ids
        assert b_id not in ids


    async def test_search_by_name_matches_store_name(
        self, seller_store_read_service, seed_full_store,
    ):
        match_id, _ = await seed_full_store(store_name="배고픈가게")
        miss_id, _ = await seed_full_store(store_name="배부른가게")

        result, _ = await seller_store_read_service.search_by_name(
            search_name="배고픈", offset=0, limit=4,
        )
        ids = {s.store_id for s in result}
        assert match_id in ids
        assert miss_id not in ids


class TestGetByStoreIds:

    async def test_returns_only_requested_ids_with_full_info(
        self, seller_store_read_service, seed_full_store,
    ):
        kept_id, _ = await seed_full_store()
        skipped_id, _ = await seed_full_store()

        results = await seller_store_read_service.get_by_store_ids([kept_id])
        ids = {s.store_id for s in results}
        assert ids == {kept_id}
        # full info eager-load 확인.
        [store] = results
        assert store.address is not None
        assert len(store.products) == 1


    async def test_empty_ids_returns_empty(self, seller_store_read_service):
        assert await seller_store_read_service.get_by_store_ids([]) == []
