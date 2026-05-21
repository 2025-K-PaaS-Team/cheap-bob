"""Tests for ``app.domain.auth.service.account.AuthAccountService``."""
from types import SimpleNamespace
import pytest

from app.domain.auth.service.exception import CustomerNotFoundError, SellerNotFoundError


@pytest.mark.unit
class TestSetCustomerActive:

    async def test_raises_when_customer_missing(self, service, customer_repo_mock):
        customer_repo_mock.find_by_email.return_value = None

        with pytest.raises(CustomerNotFoundError):
            await service.set_customer_active("missing@example.com", active=True)


    async def test_toggles_to_false_and_flushes(
        self, service, customer_repo_mock, mock_session,
    ):
        customer = SimpleNamespace(email="alice@example.com", is_active=True)
        customer_repo_mock.find_by_email.return_value = customer

        await service.set_customer_active("alice@example.com", active=False)

        assert customer.is_active is False
        mock_session.flush.assert_awaited_once()


    async def test_toggles_to_true_for_withdrawn_customer(
        self, service, customer_repo_mock,
    ):
        customer = SimpleNamespace(email="alice@example.com", is_active=False)
        customer_repo_mock.find_by_email.return_value = customer

        await service.set_customer_active("alice@example.com", active=True)

        assert customer.is_active is True


@pytest.mark.unit
class TestSetSellerActive:

    async def test_raises_when_seller_missing(self, service, seller_repo_mock):
        seller_repo_mock.find_by_email.return_value = None
        with pytest.raises(SellerNotFoundError):
            await service.set_seller_active("missing@example.com", active=True)


    async def test_toggles_and_flushes(self, service, seller_repo_mock, mock_session):
        seller = SimpleNamespace(email="bob@example.com", is_active=True)
        seller_repo_mock.find_by_email.return_value = seller

        await service.set_seller_active("bob@example.com", active=False)

        assert seller.is_active is False
        mock_session.flush.assert_awaited_once()


@pytest.mark.unit
class TestIsCustomerActive:

    async def test_raises_when_missing(self, service, customer_repo_mock):
        customer_repo_mock.find_by_email.return_value = None
        with pytest.raises(CustomerNotFoundError):
            await service.is_customer_active("missing@example.com")


    async def test_returns_current_flag(self, service, customer_repo_mock):
        customer_repo_mock.find_by_email.return_value = SimpleNamespace(is_active=False)
        assert await service.is_customer_active("alice@example.com") is False


@pytest.mark.unit
class TestIsSellerActive:

    async def test_raises_when_missing(self, service, seller_repo_mock):
        seller_repo_mock.find_by_email.return_value = None
        with pytest.raises(SellerNotFoundError):
            await service.is_seller_active("missing@example.com")


    async def test_returns_current_flag(self, service, seller_repo_mock):
        seller_repo_mock.find_by_email.return_value = SimpleNamespace(is_active=True)
        assert await service.is_seller_active("bob@example.com") is True


@pytest.mark.unit
class TestHardDeleteCustomer:
    """탈퇴 cleanup worker 호출 경로 — 단순 delegation 이지만 cascade 무결성 보장 진입점."""

    async def test_returns_repo_result_true(self, service, customer_repo_mock):
        customer_repo_mock.delete_by_email.return_value = True
        assert await service.hard_delete_customer("alice@example.com") is True
        customer_repo_mock.delete_by_email.assert_awaited_once_with("alice@example.com")


    async def test_returns_repo_result_false(self, service, customer_repo_mock):
        customer_repo_mock.delete_by_email.return_value = False
        assert await service.hard_delete_customer("missing@example.com") is False


@pytest.mark.unit
class TestHardDeleteSeller:

    async def test_returns_repo_result_true(self, service, seller_repo_mock):
        seller_repo_mock.delete_by_email.return_value = True
        assert await service.hard_delete_seller("bob@example.com") is True
        seller_repo_mock.delete_by_email.assert_awaited_once_with("bob@example.com")


    async def test_returns_repo_result_false(self, service, seller_repo_mock):
        seller_repo_mock.delete_by_email.return_value = False
        assert await service.hard_delete_seller("missing@example.com") is False
