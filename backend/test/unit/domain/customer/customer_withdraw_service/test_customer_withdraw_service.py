"""Tests for ``app.domain.customer.service.customer_withdraw.CustomerWithdrawService``."""
from types import SimpleNamespace
import pytest

from app.domain.auth.service.exception import (
    CustomerNotFoundError as AuthCustomerNotFoundError,
)
from app.domain.customer.service.exception import (
    CustomerActiveOrdersExistError,
    CustomerAlreadyActiveError,
    CustomerAlreadyWithdrawnError,
    CustomerNotFoundError,
    WithdrawalRecordNotFoundError,
)


@pytest.mark.unit
class TestRequestWithdraw:

    async def test_raises_when_already_withdrawn(self, service, auth_account_mock):
        auth_account_mock.is_customer_active.return_value = False
        with pytest.raises(CustomerAlreadyWithdrawnError):
            await service.request_withdraw("alice@example.com")


    async def test_raises_when_customer_missing(self, service, auth_account_mock):
        auth_account_mock.is_customer_active.side_effect = AuthCustomerNotFoundError("x")
        with pytest.raises(CustomerNotFoundError):
            await service.request_withdraw("alice@example.com")


    async def test_raises_when_active_orders_exist(
        self, service, auth_account_mock, order_query_mock,
    ):
        auth_account_mock.is_customer_active.return_value = True
        order_query_mock.has_active_orders_for_customer.return_value = True
        with pytest.raises(CustomerActiveOrdersExistError):
            await service.request_withdraw("alice@example.com")


    async def test_happy_path_deactivates_and_records(
        self, service, auth_account_mock, order_query_mock, withdraw_repo_mock,
    ):
        auth_account_mock.is_customer_active.return_value = True
        order_query_mock.has_active_orders_for_customer.return_value = False

        await service.request_withdraw("alice@example.com")

        auth_account_mock.set_customer_active.assert_awaited_once_with(
            "alice@example.com", active=False,
        )
        withdraw_repo_mock.save.assert_awaited_once()


@pytest.mark.unit
class TestCancelWithdraw:

    async def test_raises_when_already_active(self, service, auth_account_mock):
        auth_account_mock.is_customer_active.return_value = True
        with pytest.raises(CustomerAlreadyActiveError):
            await service.cancel_withdraw("alice@example.com")


    async def test_raises_when_customer_missing(self, service, auth_account_mock):
        auth_account_mock.is_customer_active.side_effect = AuthCustomerNotFoundError("x")
        with pytest.raises(CustomerNotFoundError):
            await service.cancel_withdraw("alice@example.com")


    async def test_raises_when_no_reservation(
        self, service, auth_account_mock, withdraw_repo_mock,
    ):
        auth_account_mock.is_customer_active.return_value = False
        withdraw_repo_mock.find_by_customer_email.return_value = None
        with pytest.raises(WithdrawalRecordNotFoundError):
            await service.cancel_withdraw("alice@example.com")


    async def test_happy_path_reactivates_and_removes_record(
        self, service, auth_account_mock, withdraw_repo_mock,
    ):
        auth_account_mock.is_customer_active.return_value = False
        withdraw_repo_mock.find_by_customer_email.return_value = SimpleNamespace()

        await service.cancel_withdraw("alice@example.com")

        auth_account_mock.set_customer_active.assert_awaited_once_with(
            "alice@example.com", active=True,
        )
        withdraw_repo_mock.delete_by_customer_email.assert_awaited_once()


@pytest.mark.unit
class TestProcessPendingWithdrawals:

    async def test_empty_returns_zero(self, service, withdraw_repo_mock):
        withdraw_repo_mock.get_many.return_value = []
        assert await service.process_pending_withdrawals() == 0


    async def test_counts_only_actually_deleted(
        self, service, withdraw_repo_mock, auth_account_mock,
    ):
        # 2건의 reservation; 첫 건만 hard_delete=True, 두 번째는 False (이미 존재 X).
        withdraw_repo_mock.get_many.return_value = [
            SimpleNamespace(id="A", customer_email="alice@example.com"),
            SimpleNamespace(id="B", customer_email="bob@example.com"),
        ]
        auth_account_mock.hard_delete_customer.side_effect = [True, False]

        processed = await service.process_pending_withdrawals()

        assert processed == 1
        # 양쪽 모두 reservation 은 정리.
        assert withdraw_repo_mock.delete_by_id.await_count == 2


    async def test_swallows_per_item_errors(
        self, service, withdraw_repo_mock, auth_account_mock,
    ):
        withdraw_repo_mock.get_many.return_value = [
            SimpleNamespace(id="A", customer_email="alice@example.com"),
            SimpleNamespace(id="B", customer_email="bob@example.com"),
        ]
        # 첫 건은 예외, 두 번째는 성공.
        auth_account_mock.hard_delete_customer.side_effect = [
            RuntimeError("boom"), True,
        ]

        processed = await service.process_pending_withdrawals()

        # 첫 건 실패는 swallow, 두 번째 성공만 카운트.
        assert processed == 1
