from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base


class StoreProductInfo(Base):
    """ 가게 상품 정보 """
    __tablename__ = "store_product_info"
    
    product_id = Column(String(255), primary_key=True) # 상품 고유 ID
    store_id = Column(String(255), ForeignKey("stores.store_id"), nullable=False) # 가게 ID
    product_name = Column(String(255), nullable=False) # 상품 이름
    description = Column(String(1000)) # 상품 설명
    initial_stock = Column(Integer, nullable=False) # 상품 설정 수량
    current_stock = Column(Integer, nullable=False) # 현재 남은 상품 수량
    price = Column(Integer, nullable=False)  # 원 단위
    sale = Column(Integer)  # 세일 퍼센트, nullable
    version = Column(Integer, default=1, nullable=False)  # 낙관적 락
    
    # Relationships
    store = relationship("Store", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_current_items = relationship("OrderCurrentItem", back_populates="product")
    nutrition_info = relationship("ProductNutrition", back_populates="product", cascade="all, delete-orphan")