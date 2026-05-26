from test.unit.domain.customer.customer_detail_service.mock_factory import (
    CustomerDetailRepoMockFactory,
    FakeUnitOfWork,
    make_mock_session,
)
import pytest

from app.domain.customer.service.customer_detail import CustomerDetailService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def detail_repo_mock():
    return CustomerDetailRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, detail_repo_mock):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_detail.CustomerDetailRepository",
        lambda session: detail_repo_mock,
    )
    return CustomerDetailService(uow=FakeUnitOfWork(mock_session))
