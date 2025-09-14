from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database.session import Base
from schemas.food_preferences import NutritionType

# 공통 ENUM 타입 정의
nutrition_type_enum = Enum(
    NutritionType,
    name='nutritiontype',
    create_type=False,  # 이미 존재하는 타입 사용
    native_enum=True
)

class ProductNutrition(Base):
    """ 상품 영양 정보 """
    __tablename__ = "product_nutrition"
    
    product_id = Column(String(255), ForeignKey("store_product_info.product_id"), primary_key=True) # 상품 ID
    nutrition_type = Column(nutrition_type_enum, primary_key=True) # 영양 타입
    
    # Relationships
    product = relationship("StoreProductInfo", back_populates="nutrition_info")