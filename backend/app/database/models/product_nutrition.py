from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database.session import Base
from schemas.food_preferences import NutritionType

class ProductNutrition(Base):
    """ 상품 영양 정보 """
    __tablename__ = "product_nutrition"
    
    product_id = Column(String(255), ForeignKey("store_product_info.product_id"), primary_key=True) # 상품 ID
    nutrition_type = Column(Enum(NutritionType), primary_key=True) # 영양 타입
    
    # Relationships
    product = relationship("StoreProductInfo", back_populates="nutrition_info")