from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from database.session import Base


class Seller(Base):
    __tablename__ = "sellers"
    
    email = Column(String(255), index=True, primary_key=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())