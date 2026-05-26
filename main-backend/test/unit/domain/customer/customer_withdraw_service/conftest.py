from test.unit.domain.customer.customer_withdraw_service.mock_factory import (
    CustomerAccountServiceMockFactory,
    FakeUnitOfWork,
    OrderQueryServiceMockFactory,
    WithdrawRepoMockFactory,
)
import pytest

from app.domain.customer.service.customer_withdraw import CustomerWithdrawService


@pytest.fixture
def withdraw_repo_mock():
    return WithdrawRepoMockFactory.create()


@pytest.fixture
def order_query_mock():
    return OrderQueryServiceMockFactory.create()


@pytest.fixture
def customer_account_mock():
    return CustomerAccountServiceMockFactory.create()


@pytest.fixture
def service(withdraw_repo_mock, order_query_mock, customer_account_mock):
    return CustomerWithdrawService(
        uow=FakeUnitOfWork(),
        withdraw_repo=withdraw_repo_mock,
        order_query_service=order_query_mock,
        customer_account_service=customer_account_mock,
    )
