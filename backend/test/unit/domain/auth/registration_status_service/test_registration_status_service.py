"""Tests for ``app.domain.auth.service.registration_status.RegistrationStatusService``."""
import pytest

from app.domain.auth.dto.auth import UserType


@pytest.mark.unit
class TestGetStatus:

    async def test_dispatches_to_customer_service(
        self, service, customer_status_mock, seller_status_mock,
    ):
        customer_status_mock.get_status.return_value = "complete"

        status = await service.get_status(
            email="alice@example.com", user_type=UserType.CUSTOMER,
        )

        assert status == "complete"
        customer_status_mock.get_status.assert_awaited_once_with("alice@example.com")
        seller_status_mock.get_status.assert_not_awaited()


    async def test_dispatches_to_seller_service(
        self, service, customer_status_mock, seller_status_mock,
    ):
        seller_status_mock.get_status.return_value = "product"

        status = await service.get_status(
            email="bob@example.com", user_type=UserType.SELLER,
        )

        assert status == "product"
        seller_status_mock.get_status.assert_awaited_once_with("bob@example.com")
        customer_status_mock.get_status.assert_not_awaited()
