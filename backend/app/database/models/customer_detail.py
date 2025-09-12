from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class CustomerDetail(Base):
    """고객 상세 정보"""
    __tablename__ = "customer_details"
    
    customer_email = Column(String(255), ForeignKey("customers.email"), primary_key=True)
    nickname = Column(String(7), nullable=False)  # 1-7자, 중복 가능
    phone_number = Column(String(11), nullable=False)  # 11자리 전화번호
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="detail")