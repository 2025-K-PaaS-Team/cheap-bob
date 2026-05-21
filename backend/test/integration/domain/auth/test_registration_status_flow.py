"""RegistrationStatusService 의 실 DB 흐름.

비즈니스 시나리오:
  1) customer 분기 — detail 미등록 → "profile", 등록 후 "complete"
  2) seller 분기 — store 미등록 → "store", store 만 → "product", product 까지 → "complete"
"""
import pytest
import pytest_asyncio

from app.domain.auth.dto.auth import UserType
from app.domain.auth.service.registration_status import RegistrationStatusService
from app.domain.customer.service.customer_registration_status import (
    CustomerRegistrationStatusService,
)
from app.domain.seller.service.seller_registration_status import (
    SellerRegistrationStatusService,
)


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def registration_status_service(uow):
    return RegistrationStatusService(
        uow=uow,
        customer_registration_status_service=CustomerRegistrationStatusService(uow=uow),
        seller_registration_status_service=SellerRegistrationStatusService(uow=uow),
    )


class TestCustomerStatus:

    async def test_returns_profile_when_no_detail(
        self, registration_status_service, session_factory,
    ):
        from app.domain.customer.model.customer import Customer
        async with session_factory() as session:
            session.add(Customer(email="newbie@example.com", is_active=True))
            await session.commit()

        status = await registration_status_service.get_status(
            email="newbie@example.com", user_type=UserType.CUSTOMER,
        )
        assert status == "profile"


    async def test_returns_complete_when_detail_exists(
        self, registration_status_service, seed_customer,
    ):
        # seed_customer 는 Customer + CustomerDetail 한 세트를 만든다.
        [email] = await seed_customer(1)

        status = await registration_status_service.get_status(
            email=email, user_type=UserType.CUSTOMER,
        )
        assert status == "complete"


class TestSellerStatus:

    async def test_returns_store_when_no_store(
        self, registration_status_service, seed_seller,
    ):
        [email] = await seed_seller(1)

        status = await registration_status_service.get_status(
            email=email, user_type=UserType.SELLER,
        )
        assert status == "store"


    async def test_returns_product_when_store_only(
        self, registration_status_service, seed_seller, session_factory,
    ):
        [email] = await seed_seller(1)

        from app.domain.seller.model.store import Store
        async with session_factory() as session:
            session.add(Store(
                store_id="STR_status_01", store_name="가게", seller_email=email,
            ))
            await session.commit()

        status = await registration_status_service.get_status(
            email=email, user_type=UserType.SELLER,
        )
        assert status == "product"


    async def test_returns_complete_when_product_exists(
        self, registration_status_service, seed_seller, session_factory,
    ):
        [email] = await seed_seller(1)

        from app.domain.seller.model.store import Store
        from app.domain.seller.model.store_product_info import StoreProductInfo
        async with session_factory() as session:
            session.add(Store(
                store_id="STR_status_02", store_name="가게", seller_email=email,
            ))
            await session.flush()
            session.add(StoreProductInfo(
                product_id="PRD_status_02",
                store_id="STR_status_02",
                product_name="상품",
                initial_stock=10,
                price=10000,
            ))
            await session.commit()

        status = await registration_status_service.get_status(
            email=email, user_type=UserType.SELLER,
        )
        assert status == "complete"
