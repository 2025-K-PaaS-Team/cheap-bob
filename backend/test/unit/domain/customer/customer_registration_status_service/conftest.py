from test.unit.domain.customer.customer_registration_status_service.mock_factory import (
    DetailRepoMockFactory,
    FakeUnitOfWork,
    make_mock_session,
)
import pytest

from app.domain.customer.service.customer_registration_status import (
    CustomerRegistrationStatusService,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def detail_repo_mock():
    return DetailRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, detail_repo_mock):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_registration_status.CustomerDetailRepository",
        lambda s: detail_repo_mock,
    )
    return CustomerRegistrationStatusService(uow=FakeUnitOfWork(mock_session))
