from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class Customer(Base):
    __tablename__ = "customers"
    
    email = Column(String(255), index=True, primary_key=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    detail = relationship("CustomerDetail", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    preferred_menus = relationship("CustomerPreferredMenu", back_populates="customer", cascade="all, delete-orphan")
    nutrition_types = relationship("CustomerNutritionType", back_populates="customer", cascade="all, delete-orphan")
    allergies = relationship("CustomerAllergy", back_populates="customer", cascade="all, delete-orphan")
    topping_types = relationship("CustomerToppingType", back_populates="customer", cascade="all, delete-orphan")
    favorites = relationship("CustomerFavorite", back_populates="customer", cascade="all, delete-orphan")