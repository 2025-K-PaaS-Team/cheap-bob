"""Tests for ``app.domain.seller.service.seller_store_profile.SellerStoreProfileService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import StoreNotFoundError


@pytest.mark.unit
class TestUpdates:

    async def test_missing_store_raises(self, service, store_repo_mock):
        store_repo_mock.update.return_value = None
        with pytest.raises(StoreNotFoundError):
            await service.update_name("STR_x", "새이름")


    async def test_each_setter_passes_keyword(self, service, store_repo_mock):
        store_repo_mock.update.return_value = SimpleNamespace(store_id="STR_x")

        await service.update_name("STR_x", "n")
        store_repo_mock.update.assert_awaited_with("STR_x", store_name="n")

        await service.update_introduction("STR_x", "i")
        store_repo_mock.update.assert_awaited_with("STR_x", store_introduction="i")

        await service.update_phone("STR_x", "p")
        store_repo_mock.update.assert_awaited_with("STR_x", store_phone="p")
