"""SellerStoreRegisterService 의 실 DB 흐름.

비즈니스 시나리오:
  1) 첫 ``register`` 호출이 Store + Address + SNS + Operation 한 트랜잭션에 생성
  2) 같은 seller 의 두 번째 ``register`` → ``StoreAlreadyRegisteredError``
  3) ``sns_info=None`` 이면 StoreSNS row 가 생기지 않는다
"""
from datetime import time
import pytest
import pytest_asyncio

from app.domain.seller.service.exception import StoreAlreadyRegisteredError
from app.domain.seller.service.seller_store_register import SellerStoreRegisterService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def seller_store_register_service(uow):
    return SellerStoreRegisterService(uow=uow)


def _default_operation_times() -> list[dict]:
    """월요일 하나만. open/close/pickup 검증 통과하는 값."""
    return [{
        "day_of_week": 0,
        "open_time": time(10, 0),
        "close_time": time(22, 0),
        "pickup_start_time": time(11, 0),
        "pickup_end_time": time(21, 0),
        "is_open_enabled": True,
    }]


class TestRegister:

    async def test_creates_store_with_full_info(
        self, seller_store_register_service, seed_seller, session_factory,
    ):
        [seller_email] = await seed_seller(1)

        store = await seller_store_register_service.register(
            seller_email=seller_email,
            store_name="첫번째가게",
            store_introduction="소개",
            store_phone="02-1234-5678",
            store_postal_code="06236",
            store_address="강남구",
            store_detail_address="101호",
            sido="서울특별시",
            sigungu="강남구",
            bname="역삼동",
            lat="37.5",
            lng="127.0",
            nearest_station="역삼역",
            walking_time=3,
            sns_info={"instagram": "https://ig.example/x"},
            operation_times=_default_operation_times(),
        )

        from app.domain.seller.model.store import Store
        from app.domain.seller.model.store_operation_info import StoreOperationInfo
        from app.domain.seller.model.store_sns import StoreSNS
        from sqlalchemy import select
        async with session_factory() as session:
            assert await session.get(Store, store.store_id) is not None
            ops = (await session.execute(
                select(StoreOperationInfo).where(
                    StoreOperationInfo.store_id == store.store_id,
                ),
            )).scalars().all()
            assert len(ops) == 1
            sns = (await session.execute(
                select(StoreSNS).where(StoreSNS.store_id == store.store_id),
            )).scalar_one_or_none()
            assert sns is not None and sns.instagram == "https://ig.example/x"


    async def test_creates_no_sns_row_when_omitted(
        self, seller_store_register_service, seed_seller, session_factory,
    ):
        [seller_email] = await seed_seller(1)

        store = await seller_store_register_service.register(
            seller_email=seller_email,
            store_name="가게",
            store_introduction="",
            store_phone="",
            store_postal_code="",
            store_address="",
            store_detail_address="",
            sido="서울특별시",
            sigungu="강남구",
            bname="역삼동",
            lat="37.5",
            lng="127.0",
            nearest_station=None,
            walking_time=None,
            sns_info=None,
            operation_times=_default_operation_times(),
        )

        from app.domain.seller.model.store_sns import StoreSNS
        from sqlalchemy import select
        async with session_factory() as session:
            sns = (await session.execute(
                select(StoreSNS).where(StoreSNS.store_id == store.store_id),
            )).scalar_one_or_none()
            assert sns is None


    async def test_double_register_raises(
        self, seller_store_register_service, seed_seller,
    ):
        [seller_email] = await seed_seller(1)
        kwargs = dict(
            seller_email=seller_email,
            store_name="중복",
            store_introduction="",
            store_phone="",
            store_postal_code="",
            store_address="",
            store_detail_address="",
            sido="서울특별시",
            sigungu="강남구",
            bname="역삼동",
            lat="37.5",
            lng="127.0",
            nearest_station=None,
            walking_time=None,
            sns_info=None,
            operation_times=_default_operation_times(),
        )

        await seller_store_register_service.register(**kwargs)
        with pytest.raises(StoreAlreadyRegisteredError):
            await seller_store_register_service.register(**kwargs)
