"""Tests for ``app.domain.order.service.product_stock_reservation.ProductStockReservationService``."""
from types import SimpleNamespace
import pytest

from app.domain.order.service.exception import ProductStockReservationNotFoundError


@pytest.mark.unit
class TestGet:

    async def test_returns_reservation_when_exists(self, service, reservation_repo_mock):
        reservation = SimpleNamespace(product_id="PRD_x", initial_stock=10, new_stock=5)
        reservation_repo_mock.get_by_product_id.return_value = reservation

        result = await service.get("PRD_x")

        assert result is reservation
        reservation_repo_mock.get_by_product_id.assert_awaited_once_with("PRD_x")


    async def test_raises_when_missing(self, service, reservation_repo_mock):
        reservation_repo_mock.get_by_product_id.return_value = None
        with pytest.raises(ProductStockReservationNotFoundError):
            await service.get("PRD_missing")


@pytest.mark.unit
class TestFind:
    """find 는 미존재 시 raise 하지 않고 None 을 그대로 돌려준다."""

    async def test_returns_none_when_missing(self, service, reservation_repo_mock):
        reservation_repo_mock.get_by_product_id.return_value = None
        assert await service.find("PRD_x") is None


    async def test_returns_reservation_when_exists(self, service, reservation_repo_mock):
        reservation = SimpleNamespace(product_id="PRD_x")
        reservation_repo_mock.get_by_product_id.return_value = reservation
        assert await service.find("PRD_x") is reservation


@pytest.mark.unit
class TestUpsert:

    async def test_delegates_to_repo_with_kwargs(self, service, reservation_repo_mock):
        await service.upsert(product_id="PRD_x", initial_stock=10, new_stock=5)
        reservation_repo_mock.create_reservation.assert_awaited_once_with(
            product_id="PRD_x", initial_stock=10, new_stock=5,
        )


@pytest.mark.unit
class TestDelete:

    async def test_raises_when_not_found(self, service, reservation_repo_mock):
        reservation_repo_mock.delete_by_product_id.return_value = False
        with pytest.raises(ProductStockReservationNotFoundError):
            await service.delete("PRD_missing")


    async def test_returns_none_when_deleted(self, service, reservation_repo_mock):
        reservation_repo_mock.delete_by_product_id.return_value = True
        assert await service.delete("PRD_x") is None


@pytest.mark.unit
class TestDeleteSilently:
    """worker 가 쓰는 silent delete — 결과 boolean 을 그대로 전달."""

    async def test_returns_false_when_missing(self, service, reservation_repo_mock):
        reservation_repo_mock.delete_by_product_id.return_value = False
        assert await service.delete_silently("PRD_x") is False


    async def test_returns_true_when_deleted(self, service, reservation_repo_mock):
        reservation_repo_mock.delete_by_product_id.return_value = True
        assert await service.delete_silently("PRD_x") is True


@pytest.mark.unit
class TestGetAll:

    async def test_returns_empty_list(self, service, reservation_repo_mock):
        reservation_repo_mock.get_all_reservations.return_value = []
        assert await service.get_all() == []


    async def test_returns_repo_result(self, service, reservation_repo_mock):
        items = [SimpleNamespace(product_id=f"PRD_{i}") for i in range(3)]
        reservation_repo_mock.get_all_reservations.return_value = items
        assert await service.get_all() == items
