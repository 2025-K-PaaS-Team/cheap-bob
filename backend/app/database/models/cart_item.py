from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class CartItem(Base):
    """ 장바구니 - 임시 재고 차감 """
    __tablename__ = "cart_items"
    
    payment_id = Column(String(255), primary_key=True) # 구매 고유 ID 
    product_id = Column(String(255), ForeignKey("store_product_info.product_id"), nullable=False) # 상품 고유 ID
    user_id = Column(String(255), nullable=False)  #  유저 고유 ID
    quantity = Column(Integer, nullable=False) # 구매 수량
    price = Column(Integer, nullable=False)  # 최종 가격 (원)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 구매 시간
    
    # Relationships
    product = relationship("StoreProductInfo", back_populates="cart_items")