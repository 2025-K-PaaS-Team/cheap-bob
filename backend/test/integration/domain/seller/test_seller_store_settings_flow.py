"""SellerStoreSettingsService 의 실 DB 흐름.

비즈니스 시나리오:
  1) ``update_address`` 가 store + address 양쪽 컬럼을 atomic 으로 갱신
  2) 미존재 store → ``StoreNotFoundError``
  3) ``list_operation`` 이 요일별 ops 정렬해서 반환
  4) ``upsert_operation_modifications`` 가 없을 때 create batch, 있을 때 update batch 분기
  5) ``delete_operation_modifications`` 가 존재하지 않으면 ``StoreOperationReservationNotFoundError``
"""
from datetime import time
import pytest
import pytest_asyncio

from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.seller.service.exception import (
    StoreNotFoundError,
    StoreOperationReservationNotFoundError,
)
from app.domain.seller.service.seller_store_settings import SellerStoreSettingsService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def seller_store_settings_service(uow):
    return SellerStoreSettingsService(
        uow=uow,
        store_payment_info_service=StorePaymentInfoService(uow=uow),
    )


def _seven_day_modifications() -> list[dict]:
    """월~일 7요일 분의 변경 데이터. CheckConstraint 충족 시간으로."""
    return [{
        "day_of_week": d,
        "open_time": time(9, 0),
        "close_time": time(22, 0),
        "pickup_start_time": time(11, 0),
        "pickup_end_time": time(21, 0),
        "is_open_enabled": True,
    } for d in range(7)]


@pytest_asyncio.fixture
async def seed_store_with_address(session_factory, seed_seller):
    from app.domain.seller.model.store import Store
    from app.domain.seller.model.store_address import StoreAddress

    counter = {"value": 0}

    async def _seed() -> str:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            address = StoreAddress(
                sido="서울특별시", sigungu="강남구", bname="역삼동",
                lat="37.5", lng="127.0",
            )
            session.add(address)
            await session.flush()
            store_id = f"STR_set_{idx:03d}"
            session.add(Store(
                store_id=store_id, store_name="가게",
                seller_email=seller_email, address_id=address.address_id,
            ))
            await session.commit()
        return store_id

    return _seed


@pytest_asyncio.fixture
async def seed_store_with_seven_ops(session_factory, seed_seller):
    """upsert_operation_modifications 가 모든 7요일 ops 를 요구하므로."""
    from app.domain.seller.model.store import Store
    from app.domain.seller.model.store_operation_info import StoreOperationInfo

    counter = {"value": 0}

    async def _seed() -> str:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_ops_{idx:03d}"
            session.add(Store(
                store_id=store_id, store_name="가게", seller_email=seller_email,
            ))
            await session.flush()
            for d in range(7):
                session.add(StoreOperationInfo(
                    store_id=store_id,
                    day_of_week=d,
                    open_time=time(10, 0),
                    close_time=time(20, 0),
                    pickup_start_time=time(11, 0),
                    pickup_end_time=time(19, 0),
                    is_open_enabled=True,
                    is_currently_open=False,
                ))
            await session.commit()
        return store_id

    return _seed


class TestUpdateAddress:

    async def test_updates_store_and_address_atomic(
        self, seller_store_settings_service, seed_store_with_address, session_factory,
    ):
        store_id = await seed_store_with_address()

        updated = await seller_store_settings_service.update_address(
            store_id=store_id,
            postal_code="06236",
            address="새주소",
            detail_address="201호",
            sido="서울특별시",
            sigungu="서초구",
            bname="서초동",
            lat="37.49",
            lng="127.02",
            nearest_station="서초역",
            walking_time=5,
        )
        assert updated.store_address == "새주소"

        # address 도 갱신됐는지.
        from app.domain.seller.model.store import Store
        from app.domain.seller.model.store_address import StoreAddress
        async with session_factory() as session:
            store = await session.get(Store, store_id)
            address = await session.get(StoreAddress, store.address_id)
            assert address.sigungu == "서초구"
            assert address.bname == "서초동"


    async def test_missing_store_raises(self, seller_store_settings_service):
        with pytest.raises(StoreNotFoundError):
            await seller_store_settings_service.update_address(
                store_id="STR_missing",
                postal_code="", address="", detail_address="",
                sido="서울특별시", sigungu="강남구", bname="역삼동",
                lat="37.5", lng="127.0",
                nearest_station=None, walking_time=None,
            )


class TestListOperation:

    async def test_returns_all_days_sorted(
        self, seller_store_settings_service, seed_store_with_seven_ops,
    ):
        store_id = await seed_store_with_seven_ops()

        ops = await seller_store_settings_service.list_operation(store_id)
        assert [o.day_of_week for o in ops] == [0, 1, 2, 3, 4, 5, 6]


class TestOperationModifications:

    async def test_upsert_creates_when_absent_then_updates(
        self, seller_store_settings_service, seed_store_with_seven_ops, session_factory,
    ):
        store_id = await seed_store_with_seven_ops()

        # 첫 호출 → create batch.
        await seller_store_settings_service.upsert_operation_modifications(
            store_id=store_id, modifications=_seven_day_modifications(),
        )

        mods = await seller_store_settings_service.list_operation_modifications(store_id)
        assert len(mods) == 7

        # 두 번째 호출 → update batch.
        updated_data = _seven_day_modifications()
        for d in updated_data:
            d["open_time"] = time(8, 0)
        await seller_store_settings_service.upsert_operation_modifications(
            store_id=store_id, modifications=updated_data,
        )

        mods = await seller_store_settings_service.list_operation_modifications(store_id)
        assert len(mods) == 7
        assert all(m.new_open_time == time(8, 0) for m in mods)


    async def test_delete_returns_when_present(
        self, seller_store_settings_service, seed_store_with_seven_ops,
    ):
        store_id = await seed_store_with_seven_ops()
        await seller_store_settings_service.upsert_operation_modifications(
            store_id=store_id, modifications=_seven_day_modifications(),
        )

        await seller_store_settings_service.delete_operation_modifications(store_id)
        assert (
            await seller_store_settings_service.list_operation_modifications(store_id)
            == []
        )


    async def test_delete_raises_when_absent(
        self, seller_store_settings_service, seed_store_with_seven_ops,
    ):
        store_id = await seed_store_with_seven_ops()
        with pytest.raises(StoreOperationReservationNotFoundError):
            await seller_store_settings_service.delete_operation_modifications(store_id)
