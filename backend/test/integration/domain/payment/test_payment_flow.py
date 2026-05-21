"""StorePaymentInfoService 의 실 DB 흐름.

비즈니스 시나리오:
  1) seller 가 가게를 만들면 결제 정보는 비어 있음
  2) settings 에서 PortOne 자격증명을 등록 → ``get_complete_by_store`` 통과
  3) secret_key 가 빠진 부분 등록 → ``PaymentInfoIncompleteError``
  4) 같은 가게에 두 번째 등록 시도 → ``PaymentInfoAlreadyExistsError``
  5) 탈퇴 cleanup 흐름 → ``delete_by_store`` True/False
"""
import pytest
import pytest_asyncio

from app.domain.payment.service.exception import (
    PaymentInfoAlreadyExistsError,
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
)
from app.domain.payment.service.store_payment_info import StorePaymentInfoService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def seed_store(session_factory, seed_seller):
    """Store row 하나를 심고 store_id 를 돌려준다.

    StorePaymentInfo 가 ``stores.store_id`` 를 FK 로 참조하므로 사전 seed 필요.
    """
    from app.domain.seller.model.store import Store

    counter = {"value": 0}

    async def _seed() -> str:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_it_{idx:03d}"
            session.add(Store(
                store_id=store_id,
                store_name=f"가게_{idx}",
                seller_email=seller_email,
            ))
            await session.commit()
        return store_id

    return _seed


class TestRegisterAndGet:

    async def test_get_missing_raises(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)
        with pytest.raises(PaymentInfoMissingError):
            await service.get_by_store(store_id)


    async def test_register_then_get_complete(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)

        await service.register(
            store_id=store_id,
            portone_store_id="ps_real",
            portone_channel_id="pc_real",
            portone_secret_key="sk_real",
        )

        info = await service.get_complete_by_store(store_id)
        assert info.portone_store_id == "ps_real"
        assert info.portone_channel_id == "pc_real"
        assert info.portone_secret_key == "sk_real"


    async def test_register_twice_conflicts(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)

        await service.register(
            store_id=store_id,
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )
        with pytest.raises(PaymentInfoAlreadyExistsError):
            await service.register(
                store_id=store_id,
                portone_store_id="ps2", portone_channel_id="pc2", portone_secret_key="sk2",
            )


class TestHasCompleteInfo:

    async def test_false_when_no_row(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)
        assert await service.has_complete_info(store_id) is False


    async def test_true_after_full_register(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)
        await service.register(
            store_id=store_id,
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )
        assert await service.has_complete_info(store_id) is True


class TestDeleteByStore:

    async def test_returns_false_when_missing(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)
        assert await service.delete_by_store(store_id) is False


    async def test_returns_true_when_deleted(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)
        await service.register(
            store_id=store_id,
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )

        assert await service.delete_by_store(store_id) is True

        # 삭제 후엔 다시 missing.
        with pytest.raises(PaymentInfoMissingError):
            await service.get_by_store(store_id)


class TestUpdatePortoneIds:

    async def test_updates_ids_preserving_secret_key(self, uow, seed_store):
        store_id = await seed_store()
        service = StorePaymentInfoService(uow=uow)
        await service.register(
            store_id=store_id,
            portone_store_id="old_ps", portone_channel_id="old_pc", portone_secret_key="sk",
        )

        await service.update_portone_ids(
            store_id=store_id,
            portone_store_id="new_ps",
            portone_channel_id="new_pc",
        )

        info = await service.get_complete_by_store(store_id)
        assert info.portone_store_id == "new_ps"
        assert info.portone_channel_id == "new_pc"
        # secret_key 는 별도 경로라 그대로 유지.
        assert info.portone_secret_key == "sk"
