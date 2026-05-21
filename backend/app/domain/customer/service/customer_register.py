from typing import List, Optional

from app.domain.customer.service.exception import CustomerAlreadyRegisteredError
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
from app.domain.customer.model.customer_topping_type import CustomerToppingType
from app.domain.customer.model.customer_preferred_menu import CustomerPreferredMenu
from app.domain.customer.model.customer_nutrition_type import CustomerNutritionType
from app.domain.customer.model.customer_detail import CustomerDetail
from app.domain.customer.model.customer_allergy import CustomerAllergy
from app.domain.customer.dto.preference import (
    AllergyType,
    NutritionType,
    PreferredMenu,
    ToppingType,
)
from app.database.session import UnitOfWork, transactional


class CustomerRegisterService:
    """2차 회원가입 — 상세 정보 + 4종 선호를 한 트랜잭션에 묶어 등록한다."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def register(
        self,
        *,
        customer_email: str,
        nickname: str,
        phone_number: str,
        preferred_menus: Optional[List[PreferredMenu]],
        nutrition_types: Optional[List[NutritionType]],
        allergies: Optional[List[AllergyType]],
        topping_types: Optional[List[ToppingType]],
    ) -> tuple[
        CustomerDetail,
        List[CustomerPreferredMenu],
        List[CustomerNutritionType],
        List[CustomerAllergy],
        List[CustomerToppingType],
    ]:
        detail_repo = CustomerDetailRepository(self._session)

        if await detail_repo.exists_by_customer(customer_email):
            raise CustomerAlreadyRegisteredError("이미 프로필이 등록되어 있습니다")

        detail = await detail_repo.save(
            CustomerDetail(
                customer_email=customer_email,
                nickname=nickname,
                phone_number=phone_number,
            ),
        )

        menu_items: List[CustomerPreferredMenu] = []
        if preferred_menus:
            menu_items = await CustomerPreferredMenuRepository(
                self._session,
            ).save_bulk(customer_email, preferred_menus)

        nutrition_items: List[CustomerNutritionType] = []
        if nutrition_types:
            nutrition_items = await CustomerNutritionTypeRepository(
                self._session,
            ).save_bulk(customer_email, nutrition_types)

        allergy_items: List[CustomerAllergy] = []
        if allergies:
            allergy_items = await CustomerAllergyRepository(
                self._session,
            ).save_bulk(customer_email, allergies)

        topping_items: List[CustomerToppingType] = []
        if topping_types:
            topping_items = await CustomerToppingTypeRepository(
                self._session,
            ).save_bulk(customer_email, topping_types)

        return detail, menu_items, nutrition_items, allergy_items, topping_items
