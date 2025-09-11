from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base
from schemas.food_preferences import PreferredMenu, NutritionType, AllergyType


class CustomerPreferredMenu(Base):
    """고객 선호 메뉴"""
    __tablename__ = "customer_preferred_menus"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_email = Column(String(255), ForeignKey("customers.email"), nullable=False)
    menu_type = Column(Enum(PreferredMenu), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="preferred_menus")


class CustomerNutritionType(Base):
    """고객 식품 영양 타입"""
    __tablename__ = "customer_nutrition_types"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_email = Column(String(255), ForeignKey("customers.email"), nullable=False)
    nutrition_type = Column(Enum(NutritionType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="nutrition_types")


class CustomerAllergy(Base):
    """고객 알레르기/제약조건"""
    __tablename__ = "customer_allergies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_email = Column(String(255), ForeignKey("customers.email"), nullable=False)
    allergy_type = Column(Enum(AllergyType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="allergies")