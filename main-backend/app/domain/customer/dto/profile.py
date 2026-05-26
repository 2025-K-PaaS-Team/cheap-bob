from typing import List
from dataclasses import dataclass

from app.domain.customer.model.customer_topping_type import CustomerToppingType
from app.domain.customer.model.customer_preferred_menu import CustomerPreferredMenu
from app.domain.customer.model.customer_nutrition_type import CustomerNutritionType
from app.domain.customer.model.customer_detail import CustomerDetail
from app.domain.customer.model.customer_allergy import CustomerAllergy


@dataclass
class CustomerFullProfile:
    """detail + 4종 선호의 통합 dto. service → router 전달용."""
    detail: CustomerDetail
    preferred_menus: List[CustomerPreferredMenu]
    nutrition_types: List[CustomerNutritionType]
    allergies: List[CustomerAllergy]
    topping_types: List[CustomerToppingType]
