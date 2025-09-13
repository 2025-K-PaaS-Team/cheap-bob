from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class Store(Base):
    """ 가게 """
    __tablename__ = "stores"
    
    store_id = Column(String(255), primary_key=True)  # 가게 고유 ID
    store_name = Column(String(255), nullable=False)  # 가게 이름
    seller_email = Column(String(255), ForeignKey("sellers.email"), nullable=False)  # 판매자 고유 ID
    
    # 새로 추가되는 필드들
    store_introduction = Column(Text, nullable=True)  # 매장 소개
    store_phone = Column(String(20), nullable=True)  # 매장 전화번호
    store_postal_code = Column(String(10), nullable=True)  # 매장 우편번호
    store_address = Column(String(255), nullable=True)  # 매장 주소
    store_detail_address = Column(String(255), nullable=True)  # 매장 상세 주소
    
    # 주소 정보 외래키
    address_id = Column(Integer, ForeignKey("addresses.address_id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 가게 생성 시간
    
    # Relationships
    seller = relationship("Seller", backref="stores")
    payment_info = relationship("StorePaymentInfo", back_populates="store", uselist=False)
    products = relationship("StoreProductInfo", back_populates="store")
    address = relationship("Address", back_populates="stores")
    sns_info = relationship("StoreSNS", back_populates="store", uselist=False)
    images = relationship("StoreImage", back_populates="store", cascade="all, delete-orphan")
    operation_info = relationship("StoreOperationInfo", back_populates="store", cascade="all, delete-orphan")