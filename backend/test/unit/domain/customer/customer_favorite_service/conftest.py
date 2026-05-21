import pytest

from app.domain.customer.service.customer_favorite import CustomerFavoriteService

from test.unit.domain.customer.customer_favorite_service.mock_factory import (
    FakeUnitOfWork,
    FavoriteRepoMockFactory,
    StoreReadServiceMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def favorite_repo_mock():
    return FavoriteRepoMockFactory.create()


@pytest.fixture
def store_read_mock():
    return StoreReadServiceMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, favorite_repo_mock, store_read_mock):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_favorite.CustomerFavoriteRepository",
        lambda s: favorite_repo_mock,
    )
    return CustomerFavoriteService(
        uow=FakeUnitOfWork(mock_session),
        seller_store_read_service=store_read_mock,
    )
