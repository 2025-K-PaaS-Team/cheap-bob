from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Time, Integer, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class StoreOperationInfo(Base):
    """ 가게 운영 정보 (요일별) """
    __tablename__ = "store_operation_info"
    
    operation_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(255), ForeignKey("stores.store_id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0: 월요일, 1: 화요일, ..., 6: 일요일
    
    # 운영 시간
    open_time = Column(Time, nullable=False)  # 오픈 시간
    pickup_start_time = Column(Time, nullable=False)  # 픽업 시작 시간
    pickup_end_time = Column(Time, nullable=False)  # 픽업 종료 시간
    close_time = Column(Time, nullable=False)  # 마감 시간
    
    # 운영 상태
    is_open_enabled = Column(Boolean, default=True, nullable=False)  # 오픈 활성화/비활성화
    is_currently_open = Column(Boolean, default=False, nullable=False)  # 현재 오픈 상태
    
    # 타임스탬프
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="operation_info")
    modification = relationship("StoreOperationInfoModification", back_populates="operation_info", uselist=False, cascade="all, delete-orphan")
    
    # 제약 조건
    __table_args__ = (
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6"),
        CheckConstraint("open_time < close_time"),
        CheckConstraint("pickup_start_time >= open_time AND pickup_start_time < close_time"),
        CheckConstraint("pickup_end_time > pickup_start_time AND pickup_end_time <= close_time"),
        {'comment': '가게 운영 정보 (요일별)'}
    )