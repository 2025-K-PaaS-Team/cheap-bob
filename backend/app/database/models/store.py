from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class Store(Base):
    """ 가게 """
    __tablename__ = "stores"
    
    store_id = Column(String(255), primary_key=True) # 가게 고유 ID
    store_name = Column(String(255), nullable=False) # 가게 이름
    seller_email = Column(String(255), ForeignKey("sellers.email"), nullable=False) # 판매자 고유 ID
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 가게 생성 시간
    
    # Relationships
    seller = relationship("Seller", backref="stores")
    # location = relationship("StoreLocation", back_populates="store", uselist=False)
    payment_info = relationship("StorePaymentInfo", back_populates="store", uselist=False)
    products = relationship("StoreProductInfo", back_populates="store")