from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base

from schemas.order import OrderStatus



class OrderHistoryItem(Base):
    """ 주문 내역 - 영구 보관 """
    __tablename__ = "order_history_items"
    
    payment_id = Column(String(255), primary_key=True) # 구매 고유 ID
    product_id = Column(String(255), ForeignKey("store_product_info.product_id"), nullable=False) # 상품 고유 ID 
    user_id = Column(String(255), nullable=False) # 유저 고유 ID
    quantity = Column(Integer, nullable=False) # 구매 수량
    price = Column(Integer, nullable=False)  # 최종 가격 (원)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.reservation) # 상태
    reservation_at = Column(DateTime(timezone=True), server_default=func.now()) # 예약 주문 시간
    accepted_at = Column(DateTime(timezone=True))  # 주문 수락 시간
    pickup_ready_at = Column(DateTime(timezone=True))  # 픽업 준비 완료 시간
    completed_at = Column(DateTime(timezone=True))  # 픽업 완료 시간
    canceled_at = Column(DateTime(timezone=True))  # 주문 취소 시간
    
    # Relationships
    product = relationship("StoreProductInfo", back_populates="order_history_items")