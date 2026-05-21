from typing import Dict, Optional

from app.util.comma_separated import join_values
from app.domain.customer.service.exception import CustomerDetailNotFoundError
from app.domain.customer.repository.customer_topping_type import (
    CustomerToppingTypeRepository,
)
from app.domain.customer.repository.customer_preferred_menu import (
    CustomerPreferredMenuRepository,
)
from app.domain.customer.repository.customer_nutrition_type import (
    CustomerNutritionTypeRepository,
)
from app.domain.customer.repository.customer_detail import CustomerDetailRepository
from app.domain.customer.repository.customer_allergy import CustomerAllergyRepository
from app.domain.customer.dto.profile import CustomerFullProfile
from app.database.session import UnitOfWork, transactional


class CustomerProfileService:
    """전체 프로필 (detail + 4종 선호) 조회.

    auth 도메인 `Customer` 모델 import 를 피하기 위해 4종 선호 + detail 을 자식 repository
    로부터 개별 조회한 뒤 dto 로 조립한다. `selectinload` 도 내부적으로 자식 테이블마다
    별개 SELECT 를 발행하므로 쿼리 수는 거의 동일.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def get_full_profile(self, customer_email: str) -> CustomerFullProfile:
        detail = await CustomerDetailRepository(self._session).find_by_customer(
            customer_email,
        )
        if detail is None:
            raise CustomerDetailNotFoundError("소비자 상세 정보가 없습니다")
        return CustomerFullProfile(
            detail=detail,
            preferred_menus=await CustomerPreferredMenuRepository(
                self._session,
            ).find_by_customer(customer_email),
            nutrition_types=await CustomerNutritionTypeRepository(
                self._session,
            ).find_by_customer(customer_email),
            allergies=await CustomerAllergyRepository(
                self._session,
            ).find_by_customer(customer_email),
            topping_types=await CustomerToppingTypeRepository(
                self._session,
            ).find_by_customer(customer_email),
        )


    @transactional
    async def get_preference_snapshot(
        self, customer_email: str,
    ) -> Dict[str, Optional[str]]:
        """payment 가 OrderCurrentItem 에 결합할 customer 선호 스냅샷 (comma-joined).

        등록 전 / 선호 없음 / customer 부재 모두 None 으로 통일.
        """
        preferred_menus = await CustomerPreferredMenuRepository(
            self._session,
        ).find_by_customer(customer_email)
        nutrition_types = await CustomerNutritionTypeRepository(
            self._session,
        ).find_by_customer(customer_email)
        allergies = await CustomerAllergyRepository(
            self._session,
        ).find_by_customer(customer_email)
        topping_types = await CustomerToppingTypeRepository(
            self._session,
        ).find_by_customer(customer_email)
        return {
            "preferred_menus": join_values(preferred_menus, "menu_type"),
            "nutrition_types": join_values(nutrition_types, "nutrition_type"),
            "allergies": join_values(allergies, "allergy_type"),
            "topping_types": join_values(topping_types, "topping_type"),
        }
