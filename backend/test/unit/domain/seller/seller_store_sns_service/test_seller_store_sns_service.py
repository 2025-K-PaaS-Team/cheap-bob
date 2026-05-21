"""Tests for ``app.domain.seller.service.seller_store_sns.SellerStoreSNSService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import StoreSNSNotFoundError


@pytest.mark.unit
class TestGet:

    async def test_returns_none_when_missing(self, service, sns_repo_mock):
        sns_repo_mock.get_by_store_id.return_value = None
        assert await service.get("STR_x") is None


    async def test_returns_existing(self, service, sns_repo_mock):
        sns_repo_mock.get_by_store_id.return_value = SimpleNamespace(instagram="ig")
        result = await service.get("STR_x")
        assert result.instagram == "ig"


@pytest.mark.unit
class TestUpdate:

    async def test_missing_row_raises(self, service, sns_repo_mock):
        sns_repo_mock.update_and_return.return_value = None
        with pytest.raises(StoreSNSNotFoundError):
            await service.update(store_id="STR_x", instagram="https://ig/x")


    async def test_returns_updated(self, service, sns_repo_mock):
        sns_repo_mock.update_and_return.return_value = SimpleNamespace(instagram="x")
        result = await service.update(store_id="STR_x", instagram="x")
        assert result.instagram == "x"
