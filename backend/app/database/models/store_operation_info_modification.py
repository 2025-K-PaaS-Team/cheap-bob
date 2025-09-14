from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Time, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base


class StoreOperationInfoModification(Base):
    """ 가게 운영 정보 수정 예약 """
    __tablename__ = "store_operation_info_modifications"
    
    modification_id = Column(Integer, primary_key=True, autoincrement=True)
    operation_id = Column(Integer, ForeignKey("store_operation_info.operation_id"), unique=True, nullable=False)
    
    # 변경될 운영 시간
    new_open_time = Column(Time, nullable=True)  # 변경 오픈 시간
    new_pickup_start_time = Column(Time, nullable=True)  # 변경 픽업 시작 시간
    new_pickup_end_time = Column(Time, nullable=True)  # 변경 픽업 종료 시간
    new_close_time = Column(Time, nullable=True)  # 변경 마감 시간
    
    # 변경될 운영 상태
    new_is_open_enabled = Column(Boolean, nullable=True)  # 변경 오픈 활성화/비활성화

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    operation_info = relationship("StoreOperationInfo", back_populates="modification")
    
    # 제약 조건
    __table_args__ = (
        CheckConstraint("new_open_time < new_close_time", name="check_new_time_order"),
        CheckConstraint("new_pickup_start_time >= new_open_time AND new_pickup_start_time < new_close_time", name="check_new_pickup_start"),
        CheckConstraint("new_pickup_end_time > new_pickup_start_time AND new_pickup_end_time <= new_close_time", name="check_new_pickup_end"),
        {'comment': '가게 운영 정보 수정 예약'}
    )