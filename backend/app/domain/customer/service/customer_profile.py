from typing import Dict, Optional

from app.util.comma_separated import join_values
from app.domain.customer.service.exception import CustomerDetailNotFoundError
from app.domain.customer.repository.customer_profile import CustomerProfileRepository
from app.domain.auth.model.customer import Customer
from app.database.session import UnitOfWork, transactional


class CustomerProfileService:
    """전체 프로필 (detail + 4종 선호) 조회."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def get_full_profile(self, customer_email: str) -> Customer:
        repo = CustomerProfileRepository(self._session)
        customer = await repo.find_full_profile(customer_email)
        if customer is None or customer.detail is None:
            raise CustomerDetailNotFoundError("소비자 상세 정보가 없습니다")
        return customer


    @transactional
    async def get_preference_snapshot(
        self, customer_email: str,
    ) -> Dict[str, Optional[str]]:
        """payment 가 OrderCurrentItem 에 결합할 customer 선호 스냅샷 (comma-joined)."""
        customer = await CustomerProfileRepository(
            self._session,
        ).find_full_profile(customer_email)
        if customer is None:
            return {
                "preferred_menus": None,
                "nutrition_types": None,
                "allergies": None,
                "topping_types": None,
            }
        return {
            "preferred_menus": join_values(customer.preferred_menus, "menu_type"),
            "nutrition_types": join_values(customer.nutrition_types, "nutrition_type"),
            "allergies": join_values(customer.allergies, "allergy_type"),
            "topping_types": join_values(customer.topping_types, "topping_type"),
        }
