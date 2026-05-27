"""Tests for ``app.domain.seller.service.seller_withdraw.SellerWithdrawService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import (
    SellerAlreadyActiveError,
    SellerAlreadyWithdrawnError,
    SellerNotFoundError,
    SellerStoreOpenError,
    SellerWithdrawalRecordNotFoundError,
)


@pytest.mark.unit
class TestRequestWithdraw:

    async def test_raises_when_store_open_today(
        self, service, operation_repo_mock,
    ):
        operation_repo_mock.get_by_store_and_day.return_value = SimpleNamespace(
            is_currently_open=True,
        )
        with pytest.raises(SellerStoreOpenError):
            await service.request_withdraw(
                seller_email="seller@example.com", store_id="STR_x",
            )


    async def test_raises_when_already_withdrawn(
        self, service, operation_repo_mock, seller_account_mock,
    ):
        operation_repo_mock.get_by_store_and_day.return_value = None
        seller_account_mock.is_active.return_value = False
        with pytest.raises(SellerAlreadyWithdrawnError):
            await service.request_withdraw(
                seller_email="seller@example.com", store_id="STR_x",
            )


    async def test_raises_when_seller_missing(
        self, service, operation_repo_mock, seller_account_mock,
    ):
        operation_repo_mock.get_by_store_and_day.return_value = None
        seller_account_mock.is_active.side_effect = SellerNotFoundError("missing")
        with pytest.raises(SellerNotFoundError):
            await service.request_withdraw(
                seller_email="seller@example.com", store_id="STR_x",
            )


    async def test_happy_path_deactivates_and_records(
        self, service, operation_repo_mock, seller_account_mock, withdraw_repo_mock,
    ):
        operation_repo_mock.get_by_store_and_day.return_value = None
        seller_account_mock.is_active.return_value = True

        await service.request_withdraw(
            seller_email="seller@example.com", store_id="STR_x",
        )

        seller_account_mock.set_active.assert_awaited_once_with(
            "seller@example.com", active=False,
        )
        withdraw_repo_mock.save.assert_awaited_once()


@pytest.mark.unit
class TestCancelWithdraw:

    async def test_raises_when_already_active(self, service, seller_account_mock):
        seller_account_mock.is_active.return_value = True
        with pytest.raises(SellerAlreadyActiveError):
            await service.cancel_withdraw("seller@example.com")


    async def test_raises_when_no_reservation(
        self, service, seller_account_mock, withdraw_repo_mock,
    ):
        seller_account_mock.is_active.return_value = False
        withdraw_repo_mock.find_by_seller_email.return_value = None
        with pytest.raises(SellerWithdrawalRecordNotFoundError):
            await service.cancel_withdraw("seller@example.com")


    async def test_happy_path_reactivates(
        self, service, seller_account_mock, withdraw_repo_mock,
    ):
        seller_account_mock.is_active.return_value = False
        withdraw_repo_mock.find_by_seller_email.return_value = SimpleNamespace()

        await service.cancel_withdraw("seller@example.com")
        seller_account_mock.set_active.assert_awaited_once_with(
            "seller@example.com", active=True,
        )
        withdraw_repo_mock.delete_by_seller_email.assert_awaited_once()


@pytest.mark.unit
class TestProcessPendingWithdrawals:

    async def test_empty_returns_zero(self, service, withdraw_repo_mock):
        withdraw_repo_mock.get_many.return_value = []
        assert await service.process_pending_withdrawals() == 0


    async def test_hard_deletes_with_cascade(
        self,
        service,
        withdraw_repo_mock,
        seller_account_mock,
        store_repo_mock,
        product_repo_mock,
        enqueue_event_mock,
        operation_repo_mock,
        image_repo_mock,
        sns_repo_mock,
    ):
        withdraw_repo_mock.get_many.return_value = [
            SimpleNamespace(id="R1", seller_email="seller@example.com"),
        ]
        store_repo_mock.get_by_seller_email.return_value = [
            SimpleNamespace(store_id="STR_x", store_name="가게"),
        ]
        # 빈 list / None 으로 cascade 부분은 no-op.

        processed = await service.process_pending_withdrawals()

        assert processed == 1
        # payment 삭제는 outbox 이벤트로 위임 — 호출 자체와 키 필드 검증.
        enqueue_event_mock.assert_awaited_once()
        kwargs = enqueue_event_mock.await_args.kwargs
        assert kwargs["aggregate_type"] == "Store"
        assert kwargs["aggregate_id"] == "STR_x"
        assert kwargs["event_type"] == "SellerStoreWithdrawn"
        assert kwargs["topic"] == "seller.store.withdrawn"
        assert kwargs["payload"] == {
            "store_id": "STR_x", "seller_email": "seller@example.com",
        }
        store_repo_mock.delete.assert_awaited_once_with("STR_x")
        seller_account_mock.hard_delete.assert_awaited_once_with(
            "seller@example.com",
        )
        withdraw_repo_mock.delete_by_id.assert_awaited_once_with("R1")


    async def test_per_item_error_swallowed_but_still_advances(
        self, service, withdraw_repo_mock, seller_account_mock,
    ):
        withdraw_repo_mock.get_many.return_value = [
            SimpleNamespace(id="R1", seller_email="a@example.com"),
            SimpleNamespace(id="R2", seller_email="b@example.com"),
        ]
        # hard_delete 가 첫 건만 예외.
        seller_account_mock.hard_delete.side_effect = [
            RuntimeError("boom"), True,
        ]

        processed = await service.process_pending_withdrawals()

        # 첫 건 처리 중 예외 → swallow, 두 번째만 정상 카운트.
        assert processed == 1
