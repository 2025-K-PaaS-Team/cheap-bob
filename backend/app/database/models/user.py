from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.session import Base


class User(Base):
    __tablename__ = "users"
    
    email = Column(String(255), index=True, primary_key=True)
    role = Column(String(255), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())