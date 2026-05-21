import pytest

from app.domain.seller.service.seller_store_image import SellerStoreImageService

from test.unit.domain.seller.seller_store_image_service.mock_factory import (
    FakeUnitOfWork,
    ObjectStorageMockFactory,
    StoreImageRepoMockFactory,
    StoreRepoMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def image_repo_mock():
    return StoreImageRepoMockFactory.create()


@pytest.fixture
def store_repo_mock():
    return StoreRepoMockFactory.create()


@pytest.fixture
def object_storage_mock():
    return ObjectStorageMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    image_repo_mock, store_repo_mock, object_storage_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_image.StoreImageRepository",
        lambda s: image_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_image.StoreRepository",
        lambda s: store_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_image.object_storage",
        object_storage_mock,
    )
    return SellerStoreImageService(uow=FakeUnitOfWork(mock_session))
