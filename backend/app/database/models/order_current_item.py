from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base

from schemas.order import OrderStatus


class OrderCurrentItem(Base):
    """ 주문 내역 - 당일 보관 """
    __tablename__ = "order_current_items"
    
    payment_id = Column(String(255), primary_key=True) # 구매 고유 ID
    product_id = Column(String(255), ForeignKey("store_product_info.product_id"), nullable=False) # 상품 고유 ID  
    user_id = Column(String(255), nullable=False)  # 유저 고유 ID
    quantity = Column(Integer, nullable=False) # 구매 수량
    price = Column(Integer, nullable=False)  # 최종 가격 (원)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.reservation) # 상태
    reservation_at = Column(DateTime(timezone=True), server_default=func.now()) # 예약 주문 시간
    accepted_at = Column(DateTime(timezone=True))  # 주문 수락 시간
    completed_at = Column(DateTime(timezone=True))  # 픽업 완료 시간
    canceled_at = Column(DateTime(timezone=True))  # 주문 취소 시간
    cancel_reason = Column(String(500), nullable=True)  # 취소 사유
    
    # User preference fields
    preferred_menus = Column(String(500), nullable=True)  # 유저의 선호 메뉴 (콤마로 구분)
    nutrition_types = Column(String(500), nullable=True)  # 식품 영양 타입 (콤마로 구분) 
    allergies = Column(String(500), nullable=True)  # 알레르기/제약조건 (콤마로 구분)
    topping_types = Column(String(500), nullable=True)  # 선호 토핑 (콤마로 구분)
    
    # Relationships
    product = relationship("StoreProductInfo", back_populates="order_current_items")