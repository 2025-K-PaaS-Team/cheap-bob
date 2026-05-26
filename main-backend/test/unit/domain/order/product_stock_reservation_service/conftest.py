from test.unit.domain.order.product_stock_reservation_service.mock_factory import (
    ReservationRepositoryMockFactory,
)
import pytest

from app.domain.order.service.product_stock_reservation import ProductStockReservationService


@pytest.fixture
def reservation_repo_mock():
    return ReservationRepositoryMockFactory.create()


@pytest.fixture
def service(reservation_repo_mock):
    return ProductStockReservationService(reservation_repo=reservation_repo_mock)
