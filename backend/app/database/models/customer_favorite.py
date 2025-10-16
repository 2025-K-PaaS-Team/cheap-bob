from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class CustomerFavorite(Base):
    """고객 즐겨찾기 가게"""
    __tablename__ = "customer_favorites"
    
    customer_email = Column(String(255), ForeignKey("customers.email"), primary_key=True, nullable=False)
    store_id = Column(String(255), ForeignKey("stores.store_id"), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="favorites")
    store = relationship("Store", back_populates="favorited_by")