from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base


class StorePaymentInfo(Base):
    """ 가게 결제 정보 """
    __tablename__ = "store_payment_info"
    
    store_id = Column(String(255), ForeignKey("stores.store_id"), primary_key=True) # 가게 고유 ID
    portone_store_id = Column(String(255)) # 포트원 가게 ID
    portone_channel_id = Column(String(255)) # 포트원 채널 ID
    portone_secret_key = Column(String(255)) # 포트원 시크릿 키
    
    # Relationships
    store = relationship("Store", back_populates="payment_info")