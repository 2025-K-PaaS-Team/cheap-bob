from app.domain.seller.service.seller_registration_status import (
    SellerRegistrationStatusService,
)
from app.domain.customer.service.customer_registration_status import (
    CustomerRegistrationStatusService,
)
from app.domain.auth.dto.auth import UserType
from app.database.session import UnitOfWork


class RegistrationStatusService:
    """회원의 온보딩 진행 상태 판별.

    customer / seller 분기는 각 도메인의 status service 에 위임한다 (strict service-to-service).
    auth 도메인이 cross-domain 테이블을 직접 보지 않는다.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        customer_registration_status_service: CustomerRegistrationStatusService,
        seller_registration_status_service: SellerRegistrationStatusService,
    ):
        self.uow = uow
        self.customer_registration_status_service = customer_registration_status_service
        self.seller_registration_status_service = seller_registration_status_service


    async def get_status(self, *, email: str, user_type: UserType) -> str:
        if user_type == UserType.CUSTOMER:
            return await self.customer_registration_status_service.get_status(email)
        return await self.seller_registration_status_service.get_status(email)
