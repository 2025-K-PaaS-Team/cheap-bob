from typing import List

from app.domain.customer.service.exception import (
    PreferenceDuplicateError,
    PreferenceNotFoundError,
)
from app.domain.customer.repository.customer_topping_type import (
    CustomerToppingTypeRepository,
)
from app.domain.customer.repository.customer_preferred_menu import (
    CustomerPreferredMenuRepository,
)
from app.domain.customer.repository.customer_nutrition_type import (
    CustomerNutritionTypeRepository,
)
from app.domain.customer.repository.customer_allergy import CustomerAllergyRepository
from app.domain.customer.model.customer_topping_type import CustomerToppingType
from app.domain.customer.model.customer_preferred_menu import CustomerPreferredMenu
from app.domain.customer.model.customer_nutrition_type import CustomerNutritionType
from app.domain.customer.model.customer_allergy import CustomerAllergy
from app.domain.customer.dto.preference import (
    AllergyType,
    NutritionType,
    PreferredMenu,
    ToppingType,
)
from app.database.session import UnitOfWork, transactional


class CustomerPreferenceService:
    """4종 선호도 (메뉴 / 영양 / 알레르기 / 토핑) 의 GET / 일괄 추가 / 단건 삭제.

    각 타입의 동작이 동일 패턴이라 1개 서비스에서 4메서드 묶음으로 처리한다.
    "이미 등록됨" 중복 검사는 추가 직전에 한다 (race window 는 작지만 트랜잭션 내부 검사라 OK).
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    # ───────── PreferredMenu ─────────


    @transactional
    async def list_preferred_menus(
        self, customer_email: str,
    ) -> List[CustomerPreferredMenu]:
        return await CustomerPreferredMenuRepository(self._session).find_by_customer(
            customer_email,
        )


    @transactional
    async def add_preferred_menus(
        self, customer_email: str, menu_types: List[PreferredMenu],
    ) -> List[CustomerPreferredMenu]:
        repo = CustomerPreferredMenuRepository(self._session)
        existing = await repo.find_by_customer(customer_email)
        self._reject_duplicates(
            {m.menu_type for m in existing}, set(menu_types),
        )
        created = await repo.save_bulk(customer_email, menu_types)
        return existing + created


    @transactional
    async def remove_preferred_menu(
        self, customer_email: str, menu_type: PreferredMenu,
    ) -> None:
        deleted = await CustomerPreferredMenuRepository(self._session).delete(
            customer_email, menu_type,
        )
        if not deleted:
            raise PreferenceNotFoundError("해당 선호 메뉴를 찾을 수 없습니다")


    # ───────── NutritionType ─────────


    @transactional
    async def list_nutrition_types(
        self, customer_email: str,
    ) -> List[CustomerNutritionType]:
        return await CustomerNutritionTypeRepository(self._session).find_by_customer(
            customer_email,
        )


    @transactional
    async def add_nutrition_types(
        self, customer_email: str, nutrition_types: List[NutritionType],
    ) -> List[CustomerNutritionType]:
        repo = CustomerNutritionTypeRepository(self._session)
        existing = await repo.find_by_customer(customer_email)
        self._reject_duplicates(
            {n.nutrition_type for n in existing}, set(nutrition_types),
        )
        created = await repo.save_bulk(customer_email, nutrition_types)
        return existing + created


    @transactional
    async def remove_nutrition_type(
        self, customer_email: str, nutrition_type: NutritionType,
    ) -> None:
        deleted = await CustomerNutritionTypeRepository(self._session).delete(
            customer_email, nutrition_type,
        )
        if not deleted:
            raise PreferenceNotFoundError("해당 영양 타입을 찾을 수 없습니다")


    # ───────── Allergy ─────────


    @transactional
    async def list_allergies(self, customer_email: str) -> List[CustomerAllergy]:
        return await CustomerAllergyRepository(self._session).find_by_customer(
            customer_email,
        )


    @transactional
    async def add_allergies(
        self, customer_email: str, allergy_types: List[AllergyType],
    ) -> List[CustomerAllergy]:
        repo = CustomerAllergyRepository(self._session)
        existing = await repo.find_by_customer(customer_email)
        self._reject_duplicates(
            {a.allergy_type for a in existing}, set(allergy_types),
        )
        created = await repo.save_bulk(customer_email, allergy_types)
        return existing + created


    @transactional
    async def remove_allergy(
        self, customer_email: str, allergy_type: AllergyType,
    ) -> None:
        deleted = await CustomerAllergyRepository(self._session).delete(
            customer_email, allergy_type,
        )
        if not deleted:
            raise PreferenceNotFoundError("해당 알레르기를 찾을 수 없습니다")


    # ───────── ToppingType ─────────


    @transactional
    async def list_topping_types(
        self, customer_email: str,
    ) -> List[CustomerToppingType]:
        return await CustomerToppingTypeRepository(self._session).find_by_customer(
            customer_email,
        )


    @transactional
    async def add_topping_types(
        self, customer_email: str, topping_types: List[ToppingType],
    ) -> List[CustomerToppingType]:
        repo = CustomerToppingTypeRepository(self._session)
        existing = await repo.find_by_customer(customer_email)
        self._reject_duplicates(
            {t.topping_type for t in existing}, set(topping_types),
        )
        created = await repo.save_bulk(customer_email, topping_types)
        return existing + created


    @transactional
    async def remove_topping_type(
        self, customer_email: str, topping_type: ToppingType,
    ) -> None:
        deleted = await CustomerToppingTypeRepository(self._session).delete(
            customer_email, topping_type,
        )
        if not deleted:
            raise PreferenceNotFoundError("해당 토핑 타입을 찾을 수 없습니다")


    # ───────── helpers ─────────


    @staticmethod
    def _reject_duplicates(existing: set, incoming: set) -> None:
        overlap = incoming & existing
        if overlap:
            raise PreferenceDuplicateError([e.value for e in overlap])
