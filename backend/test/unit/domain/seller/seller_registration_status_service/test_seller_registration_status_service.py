"""Tests for ``SellerRegistrationStatusService``."""
from types import SimpleNamespace
import pytest


@pytest.mark.unit
class TestGetStatus:

    async def test_returns_store_when_no_store(self, service, store_repo_mock):
        store_repo_mock.get_by_seller_email.return_value = []
        assert await service.get_status("seller@example.com") == "store"


    async def test_returns_product_when_zero_products(
        self, service, store_repo_mock, product_repo_mock,
    ):
        store_repo_mock.get_by_seller_email.return_value = [
            SimpleNamespace(store_id="STR_x"),
        ]
        product_repo_mock.count_products_by_store.return_value = 0
        assert await service.get_status("seller@example.com") == "product"


    async def test_returns_complete_when_products_exist(
        self, service, store_repo_mock, product_repo_mock,
    ):
        store_repo_mock.get_by_seller_email.return_value = [
            SimpleNamespace(store_id="STR_x"),
        ]
        product_repo_mock.count_products_by_store.return_value = 3
        assert await service.get_status("seller@example.com") == "complete"
