"""StorePaymentInfoService 의 실 DB 흐름.

비즈니스 시나리오:
  1) 가게 결제 정보가 없는 상태에서 조회 → ``PaymentInfoMissingError``
  2) settings 에서 PortOne 자격증명을 등록 → ``get_complete_by_store`` 통과
  3) 같은 가게에 두 번째 등록 시도 → ``PaymentInfoAlreadyExistsError``
  4) 탈퇴 cleanup 흐름 → ``delete_by_store`` True/False
  5) PortOne ID 갱신 시 secret_key 보존

payment-backend 의 ``store_payment_info`` 는 MSA 분리 후 main-backend 의 ``stores`` 테이블에 FK 가
없다 — 다른 DB 라서 그렇다. 따라서 store row 를 미리 seed 할 필요 없이 unique 한 store_id
문자열만 있으면 된다.
"""
import pytest

from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.exception import (
    PaymentInfoAlreadyExistsError,
    PaymentInfoMissingError,
)


pytestmark = pytest.mark.integration


@pytest.fixture
def make_store_id():
    """매 호출마다 unique 한 store_id 문자열을 돌려준다.

    payment-backend DB 의 store_payment_info 는 FK 가 없으므로 실제 stores row 는 불필요.
    같은 테스트 안에서 여러 가게가 필요할 때 fixture 를 여러 번 호출하면 된다.
    """
    counter = {"value": 0}

    def _next() -> str:
        idx = counter["value"]
        counter["value"] += 1
        return f"STR_it_{idx:03d}"

    return _next


class TestRegisterAndGet:

    async def test_get_missing_raises(self, uow, make_store_id):
        service = StorePaymentInfoService(uow=uow)
        with pytest.raises(PaymentInfoMissingError):
            await service.get_by_store(make_store_id())


    async def test_register_then_get_complete(self, uow, make_store_id):
        store_id = make_store_id()
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


    async def test_register_twice_conflicts(self, uow, make_store_id):
        store_id = make_store_id()
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

    async def test_false_when_no_row(self, uow, make_store_id):
        service = StorePaymentInfoService(uow=uow)
        assert await service.has_complete_info(make_store_id()) is False


    async def test_true_after_full_register(self, uow, make_store_id):
        store_id = make_store_id()
        service = StorePaymentInfoService(uow=uow)
        await service.register(
            store_id=store_id,
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )
        assert await service.has_complete_info(store_id) is True


class TestDeleteByStore:

    async def test_returns_false_when_missing(self, uow, make_store_id):
        service = StorePaymentInfoService(uow=uow)
        assert await service.delete_by_store(make_store_id()) is False


    async def test_returns_true_when_deleted(self, uow, make_store_id):
        store_id = make_store_id()
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

    async def test_updates_ids_preserving_secret_key(self, uow, make_store_id):
        store_id = make_store_id()
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
