import pytest

from app.domain.order.service.cart_recovery import CartRecoveryService

from test.unit.domain.order.cart_recovery_service.mock_factory import (
    CartItemRepoMockFactory,
    FakeUnitOfWork,
    OrderQueryServiceMockFactory,
    SellerProductServiceMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def cart_item_repo_mock():
    return CartItemRepoMockFactory.create()


@pytest.fixture
def product_service_mock():
    return SellerProductServiceMockFactory.create()


@pytest.fixture
def order_query_mock():
    return OrderQueryServiceMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    cart_item_repo_mock, product_service_mock, order_query_mock,
):
    monkeypatch.setattr(
        "app.domain.order.service.cart_recovery.CartItemRepository",
        lambda s: cart_item_repo_mock,
        raising=False,
    )
    # `from app.domain.order.repository.cart_item import CartItemRepository` 가
    # 함수 내부 import 이므로 직접 sys.modules 의 클래스를 교체한다.
    import app.domain.order.repository.cart_item as cart_item_mod
    monkeypatch.setattr(
        cart_item_mod, "CartItemRepository", lambda s: cart_item_repo_mock,
    )
    return CartRecoveryService(
        uow=FakeUnitOfWork(mock_session),
        seller_product_service=product_service_mock,
        order_query_service=order_query_mock,
    )
