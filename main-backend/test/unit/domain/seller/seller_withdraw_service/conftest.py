from unittest.mock import AsyncMock
from test.unit.domain.seller.seller_withdraw_service.mock_factory import (
    FakeUnitOfWork,
    ImageRepoMockFactory,
    OperationRepoMockFactory,
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
def enqueue_event_mock(monkeypatch):
    """payment-backend 호출 대신 outbox 이벤트로 위임된 흐름 검증.

    seller_withdraw 가 import 한 enqueue_event 심볼을 직접 패치 — 같은 함수가 다른
    모듈에서 import 돼 있어도 본 서비스가 보는 참조만 교체된다.
    """
    mock = AsyncMock()
    monkeypatch.setattr(
        "app.domain.seller.service.seller_withdraw.enqueue_event", mock,
    )
    return mock


@pytest.fixture
def service(
    monkeypatch, mock_session,
    withdraw_repo_mock, seller_account_mock,
    store_repo_mock, product_repo_mock, operation_repo_mock,
    image_repo_mock, sns_repo_mock, enqueue_event_mock,
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
    )
