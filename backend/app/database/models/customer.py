from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from database.session import Base


class Customer(Base):
    __tablename__ = "customers"
    
    email = Column(String(255), index=True, primary_key=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())