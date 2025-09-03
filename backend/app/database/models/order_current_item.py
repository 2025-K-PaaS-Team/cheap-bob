from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base
import enum


class OrderStatus(enum.Enum):
    reservation = "reservation" # 예약 중
    complete = "complete" # 승인 완료
    cancel = "cancel" # 취소


class OrderCurrentItem(Base):
    """ 주문 내역 - 당일 보관 """
    __tablename__ = "order_current_items"
    
    payment_id = Column(String(255), primary_key=True) # 구매 고유 ID
    product_id = Column(String(255), ForeignKey("store_product_info.product_id"), nullable=False) # 상품 고유 ID  
    user_id = Column(String(255), nullable=False)  # 유저 고유 ID
    quantity = Column(Integer, nullable=False) # 구매 수량
    price = Column(Integer, nullable=False)  # 최종 가격 (원)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.reservation) # 상태
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 구매 시간
    confirmed_at = Column(DateTime(timezone=True))  # 판매자 승인 시간
    
    # Relationships
    product = relationship("StoreProductInfo", back_populates="order_current_items")