"""Tests for ``app.domain.payment.service.store_payment_info.StorePaymentInfoService``."""
from types import SimpleNamespace
import pytest

from app.domain.payment.service.exception import (
    PaymentInfoAlreadyExistsError,
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
)


@pytest.mark.unit
class TestGetByStore:

    async def test_missing_raises(self, service, payment_repo_mock):
        payment_repo_mock.get_by_store_id.return_value = None
        with pytest.raises(PaymentInfoMissingError):
            await service.get_by_store("STR_x")


    async def test_returns_when_present(self, service, payment_repo_mock):
        info = SimpleNamespace(
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )
        payment_repo_mock.get_by_store_id.return_value = info
        assert await service.get_by_store("STR_x") is info


@pytest.mark.unit
class TestGetCompleteByStore:

    async def test_incomplete_raises(self, service, payment_repo_mock):
        payment_repo_mock.get_by_store_id.return_value = SimpleNamespace(
            portone_store_id="ps", portone_channel_id=None, portone_secret_key="sk",
        )
        with pytest.raises(PaymentInfoIncompleteError):
            await service.get_complete_by_store("STR_x")


    async def test_complete_returns_info(self, service, payment_repo_mock):
        info = SimpleNamespace(
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )
        payment_repo_mock.get_by_store_id.return_value = info
        result = await service.get_complete_by_store("STR_x")
        assert result is info


@pytest.mark.unit
class TestRegister:

    async def test_duplicate_raises(self, service, payment_repo_mock):
        payment_repo_mock.exists_by_store_id.return_value = True
        with pytest.raises(PaymentInfoAlreadyExistsError):
            await service.register(
                store_id="STR_x",
                portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
            )


    async def test_passes_to_repo_create(self, service, payment_repo_mock):
        payment_repo_mock.exists_by_store_id.return_value = False
        await service.register(
            store_id="STR_x",
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )
        payment_repo_mock.create.assert_awaited_once_with(
            store_id="STR_x",
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )


@pytest.mark.unit
class TestDeleteByStore:

    async def test_returns_false_when_missing(self, service, payment_repo_mock):
        payment_repo_mock.exists_by_store_id.return_value = False
        assert await service.delete_by_store("STR_x") is False


    async def test_returns_true_after_delete(self, service, payment_repo_mock):
        payment_repo_mock.exists_by_store_id.return_value = True
        assert await service.delete_by_store("STR_x") is True
        payment_repo_mock.delete.assert_awaited_once_with("STR_x")


@pytest.mark.unit
class TestHasCompleteInfo:

    async def test_returns_repo_result(self, service, payment_repo_mock):
        payment_repo_mock.has_complete_info.return_value = True
        assert await service.has_complete_info("STR_x") is True
