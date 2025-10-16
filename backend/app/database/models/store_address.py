from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from database.session import Base


class StoreAddress(Base):
    """ 주소 정보 (시/도, 시/군/구, 읍/면/동) """
    __tablename__ = "store_addresses"
    
    address_id = Column(Integer, primary_key=True, autoincrement=True)
    sido = Column(String(50), nullable=False)  # 시/도
    sigungu = Column(String(50), nullable=False)  # 시/군/구
    bname = Column(String(50), nullable=False)  # 읍/면/동
    lat = Column(String(50), nullable=False)  # 위도
    lng = Column(String(50), nullable=False)  # 경도
    
    # Relationships
    stores = relationship("Store", back_populates="address")