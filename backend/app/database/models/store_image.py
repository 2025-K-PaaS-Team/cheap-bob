from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class StoreImage(Base):
    """ 가게 이미지 """
    __tablename__ = "store_images"
    
    image_id = Column(String(255), primary_key=True)
    store_id = Column(String(255), ForeignKey("stores.store_id"), nullable=False)
    is_main = Column(Boolean, default=False, nullable=False)  # 대표 이미지 여부
    display_order = Column(Integer, default=0, nullable=False)  # 표시 순서
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="images")