from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.session import Base


class StoreSNS(Base):
    """ 가게 SNS 정보 """
    __tablename__ = "store_sns"
    
    sns_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(255), ForeignKey("stores.store_id"), unique=True, nullable=False)
    
    # SNS 정보들 (모두 nullable)
    instagram = Column(Text, nullable=True)  # 인스타그램 URL
    facebook = Column(Text, nullable=True)   # 페이스북 URL
    x = Column(Text, nullable=True)         # X(구 트위터) URL
    homepage = Column(Text, nullable=True)   # 홈페이지 URL
    
    # Relationships
    store = relationship("Store", back_populates="sns_info")