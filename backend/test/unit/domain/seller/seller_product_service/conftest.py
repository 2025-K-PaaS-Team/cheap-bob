import pytest

from app.domain.seller.service.seller_product import SellerProductService

from test.unit.domain.seller.seller_product_service.mock_factory import (
    FakeUnitOfWork,
    ProductNutritionRepoMockFactory,
    ProductStockReservationServiceMockFactory,
    StoreProductInfoRepoMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def product_repo_mock():
    return StoreProductInfoRepoMockFactory.create()


@pytest.fixture
def nutrition_repo_mock():
    return ProductNutritionRepoMockFactory.create()


@pytest.fixture
def stock_reservation_mock():
    return ProductStockReservationServiceMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    product_repo_mock, nutrition_repo_mock, stock_reservation_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_product.StoreProductInfoRepository",
        lambda s: product_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_product.ProductNutritionRepository",
        lambda s: nutrition_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_product.generate_product_id",
        lambda: "PRD_fixed",
    )
    return SellerProductService(
        uow=FakeUnitOfWork(mock_session),
        product_stock_reservation_service=stock_reservation_mock,
    )
