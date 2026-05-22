from test.unit.domain.seller.seller_withdraw_service.mock_factory import (
    FakeUnitOfWork,
    ImageRepoMockFactory,
    OperationRepoMockFactory,
    PaymentInfoServiceMockFactory,
    ProductRepoMockFactory,
    SellerAccountServiceMockFactory,
    SnsRepoMockFactory,
    StoreRepoMockFactory,
    WithdrawRepoMockFactory,
    make_mock_session,
)
import pytest

from app.domain.seller.service.seller_withdraw import SellerWithdrawService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def withdraw_repo_mock():
    return WithdrawRepoMockFactory.create()


@pytest.fixture
def seller_account_mock():
    return SellerAccountServiceMockFactory.create()


@pytest.fixture
def payment_info_mock():
    return PaymentInfoServiceMockFactory.create()


@pytest.fixture
def store_repo_mock():
    return StoreRepoMockFactory.create()


@pytest.fixture
def product_repo_mock():
    return ProductRepoMockFactory.create()


@pytest.fixture
def operation_repo_mock():
    return OperationRepoMockFactory.create()


@pytest.fixture
def image_repo_mock():
    return ImageRepoMockFactory.create()


@pytest.fixture
def sns_repo_mock():
    return SnsRepoMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    withdraw_repo_mock, seller_account_mock, payment_info_mock,
    store_repo_mock, product_repo_mock, operation_repo_mock,
    image_repo_mock, sns_repo_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_withdraw.StoreOperationInfoRepository",
        lambda s: operation_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_withdraw.StoreRepository",
        lambda s: store_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_withdraw.StoreProductInfoRepository",
        lambda s: product_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_withdraw.StoreImageRepository",
        lambda s: image_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_withdraw.StoreSNSRepository",
        lambda s: sns_repo_mock,
    )
    return SellerWithdrawService(
        uow=FakeUnitOfWork(mock_session),
        withdraw_repo=withdraw_repo_mock,
        seller_account_service=seller_account_mock,
        store_payment_info_service=payment_info_mock,
    )
