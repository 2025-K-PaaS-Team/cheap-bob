"""Tests for ``SellerPaymentSettingsService``."""
from types import SimpleNamespace
import pytest


@pytest.mark.unit
class TestRegister:

    async def test_passes_kwargs(self, service, store_payment_info_mock):
        await service.register(
            store_id="STR_x",
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )
        store_payment_info_mock.register.assert_awaited_once_with(
            store_id="STR_x",
            portone_store_id="ps", portone_channel_id="pc", portone_secret_key="sk",
        )


@pytest.mark.unit
class TestExists:

    async def test_returns_underlying_bool(self, service, store_payment_info_mock):
        store_payment_info_mock.exists_by_store.return_value = True
        assert await service.exists("STR_x") is True


@pytest.mark.unit
class TestGetInitial:

    async def test_returns_none_fields_when_missing(
        self, service, store_payment_info_mock,
    ):
        store_payment_info_mock.find_by_store.return_value = None
        result = await service.get_initial("STR_x")
        assert result.portone_store_id is None
        assert result.portone_channel_id is None


    async def test_returns_existing_ids_without_secret(
        self, service, store_payment_info_mock,
    ):
        store_payment_info_mock.find_by_store.return_value = SimpleNamespace(
            portone_store_id="ps",
            portone_channel_id="pc",
            portone_secret_key="DO_NOT_LEAK",
        )
        result = await service.get_initial("STR_x")
        assert result.portone_store_id == "ps"
        assert result.portone_channel_id == "pc"
        # secret_key 가 응답에 포함돼선 안 됨.
        assert not hasattr(result, "portone_secret_key")


@pytest.mark.unit
class TestUpdateIds:

    async def test_calls_underlying_and_returns_response(
        self, service, store_payment_info_mock,
    ):
        result = await service.update_ids(
            store_id="STR_x", portone_store_id="new_ps", portone_channel_id="new_pc",
        )
        store_payment_info_mock.update_portone_ids.assert_awaited_once_with(
            store_id="STR_x", portone_store_id="new_ps", portone_channel_id="new_pc",
        )
        assert result.portone_store_id == "new_ps"
        assert result.portone_channel_id == "new_pc"
