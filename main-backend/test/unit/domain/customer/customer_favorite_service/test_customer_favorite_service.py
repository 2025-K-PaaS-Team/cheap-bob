"""Tests for ``app.domain.customer.service.customer_favorite.CustomerFavoriteService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.customer.service.exception import (
    FavoriteAlreadyExistsError,
    FavoriteNotFoundError,
)


@pytest.mark.unit
class TestAdd:

    async def test_raises_when_store_missing(self, service, store_read_mock):
        store_read_mock.get_with_full_info.return_value = None
        with pytest.raises(StoreNotFoundError):
            await service.add(customer_email="alice@example.com", store_id="STR_x")


    async def test_raises_when_duplicate(
        self, service, store_read_mock, favorite_repo_mock,
    ):
        store_read_mock.get_with_full_info.return_value = SimpleNamespace(
            store_id="STR_x",
        )
        favorite_repo_mock.find_by_customer_and_store.return_value = SimpleNamespace()

        with pytest.raises(FavoriteAlreadyExistsError):
            await service.add(customer_email="alice@example.com", store_id="STR_x")


    async def test_saves_when_new(
        self, service, store_read_mock, favorite_repo_mock,
    ):
        store_read_mock.get_with_full_info.return_value = SimpleNamespace(
            store_id="STR_x",
        )
        favorite_repo_mock.find_by_customer_and_store.return_value = None

        await service.add(customer_email="alice@example.com", store_id="STR_x")

        favorite_repo_mock.save.assert_awaited_once_with("alice@example.com", "STR_x")


@pytest.mark.unit
class TestRemove:

    async def test_raises_when_missing(self, service, favorite_repo_mock):
        favorite_repo_mock.delete.return_value = False
        with pytest.raises(FavoriteNotFoundError):
            await service.remove(customer_email="alice@example.com", store_id="STR_x")


    async def test_deletes_when_present(self, service, favorite_repo_mock):
        favorite_repo_mock.delete.return_value = True
        await service.remove(customer_email="alice@example.com", store_id="STR_x")
        favorite_repo_mock.delete.assert_awaited_once_with(
            "alice@example.com", "STR_x",
        )
