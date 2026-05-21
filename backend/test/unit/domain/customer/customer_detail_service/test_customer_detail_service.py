"""Tests for ``app.domain.customer.service.customer_detail.CustomerDetailService``."""
from types import SimpleNamespace
import pytest

from app.domain.customer.service.exception import CustomerDetailNotFoundError


@pytest.mark.unit
class TestGet:

    async def test_raises_when_missing(self, service, detail_repo_mock):
        detail_repo_mock.find_by_customer.return_value = None
        with pytest.raises(CustomerDetailNotFoundError):
            await service.get("alice@example.com")


    async def test_returns_detail_when_found(self, service, detail_repo_mock):
        detail = SimpleNamespace(nickname="홍", phone_number="01000000000")
        detail_repo_mock.find_by_customer.return_value = detail

        result = await service.get("alice@example.com")

        assert result is detail
        detail_repo_mock.find_by_customer.assert_awaited_once_with("alice@example.com")


@pytest.mark.unit
class TestUpdate:

    async def test_raises_when_missing(self, service, detail_repo_mock):
        detail_repo_mock.update.return_value = None
        with pytest.raises(CustomerDetailNotFoundError):
            await service.update(
                customer_email="alice@example.com",
                nickname="x",
                phone_number=None,
            )


    async def test_passes_kwargs_to_repo_and_returns_result(
        self, service, detail_repo_mock,
    ):
        updated = SimpleNamespace(nickname="새닉", phone_number="01000000000")
        detail_repo_mock.update.return_value = updated

        result = await service.update(
            customer_email="alice@example.com",
            nickname="새닉",
            phone_number=None,
        )

        assert result is updated
        detail_repo_mock.update.assert_awaited_once_with(
            "alice@example.com", nickname="새닉", phone_number=None,
        )
