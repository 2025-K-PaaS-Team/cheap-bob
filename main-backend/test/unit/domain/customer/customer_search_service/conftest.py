from test.unit.domain.customer.customer_search_service.mock_factory import (
    FakeUnitOfWork,
    FavoriteRepoMockFactory,
    StoreReadServiceMockFactory,
    make_mock_session,
)
import pytest

from app.domain.customer.service.customer_search import CustomerSearchService


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
    from datetime import datetime, timezone
    from app.domain.seller.schema.store_sns import StoreSNSInfo
    from app.domain.seller.schema.store_settings import StoreAddressResponse
    from app.domain.seller.schema.store import StoreDetailResponseForCustomer

    monkeypatch.setattr(
        "app.domain.customer.service.customer_search.CustomerFavoriteRepository",
        lambda s: favorite_repo_mock,
    )

    def _stub_convert(store, is_favorite: bool):
        # 진짜 pydantic 모델 — `PaginatedStoreResponse` 검증을 통과해야 한다.
        return StoreDetailResponseForCustomer(
            store_id=store.store_id,
            store_name="가게",
            store_introduction="",
            store_phone="",
            seller_email="seller@example.com",
            created_at=datetime.now(timezone.utc),
            address=StoreAddressResponse(
                store_id=store.store_id, postal_code="", address="",
                detail_address="", sido="", sigungu="", bname="",
                lat="0", lng="0", nearest_station=None, walking_time=None,
            ),
            sns=StoreSNSInfo(),
            operation_times=[],
            images=[],
            products=[],
            is_favorite=is_favorite,
        )

    monkeypatch.setattr(
        "app.domain.customer.service.customer_search.convert_store_to_response",
        _stub_convert,
    )
    return CustomerSearchService(
        uow=FakeUnitOfWork(mock_session),
        seller_store_read_service=store_read_mock,
    )
