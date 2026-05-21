import pytest

from app.domain.auth.service.oauth import OAuthService

from test.unit.domain.auth.oauth_service.mock_factory import (
    CustomerRepositoryMockFactory,
    FakeUnitOfWork,
    JwtServiceMockFactory,
    SellerRepositoryMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def customer_repo_mock():
    return CustomerRepositoryMockFactory.create()


@pytest.fixture
def seller_repo_mock():
    return SellerRepositoryMockFactory.create()


@pytest.fixture
def jwt_service_mock():
    return JwtServiceMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, customer_repo_mock, seller_repo_mock, jwt_service_mock):
    """OAuthService 의 모든 DB 의존성을 Mock 으로 치환한 인스턴스.

    서비스 내부에서 ``CustomerRepository(session)`` 식으로 생성자 호출하므로 모듈 레벨
    이름을 ``lambda session: repo_mock`` 으로 치환한다.
    """
    monkeypatch.setattr(
        "app.domain.auth.service.oauth.CustomerRepository",
        lambda session: customer_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.auth.service.oauth.SellerRepository",
        lambda session: seller_repo_mock,
    )
    return OAuthService(uow=FakeUnitOfWork(mock_session), jwt_service=jwt_service_mock)
