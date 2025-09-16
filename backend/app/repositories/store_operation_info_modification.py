from typing import List, Optional
from datetime import time, datetime, timezone, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from database.models.store_operation_info_modification import StoreOperationInfoModification
from database.models.store_operation_info import StoreOperationInfo
from repositories.base import BaseRepository

# KST 타임존 설정
KST = timezone(timedelta(hours=9))

# 로거 설정
logger = logging.getLogger(__name__)


class StoreOperationInfoModificationRepository(BaseRepository[StoreOperationInfoModification]):
    """가게 운영 정보 수정 예약 Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(StoreOperationInfoModification, session)
    
    async def get_by_operation_id(self, operation_id: int) -> Optional[StoreOperationInfoModification]:
        """운영 정보 ID로 수정 예약 조회"""
        return await self.get_one(operation_id=operation_id)
    
    async def get_by_store_id(self, store_id: str) -> List[StoreOperationInfoModification]:
        """가게의 모든 수정 예약 조회"""
        query = (
            select(StoreOperationInfoModification)
            .join(StoreOperationInfo)
            .where(StoreOperationInfo.store_id == store_id)
            .options(selectinload(StoreOperationInfoModification.operation_info))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_modification(
        self,
        operation_id: int,
        new_open_time: Optional[time] = None,
        new_close_time: Optional[time] = None,
        new_pickup_start_time: Optional[time] = None,
        new_pickup_end_time: Optional[time] = None,
        new_is_open_enabled: Optional[bool] = None
    ) -> Optional[StoreOperationInfoModification]:
        """수정 예약 생성"""
        
        # 운영 정보 존재 확인
        operation_info = await self.session.get(StoreOperationInfo, operation_id)
        if not operation_info:
            raise ValueError("운영 정보를 찾을 수 없습니다.")
        
        # 이미 수정 예약이 있는지 확인
        existing = await self.get_by_operation_id(operation_id)
        if existing:
            raise ValueError("이미 수정 예약이 존재합니다.")
        
        # 시간 유효성 검증 (모든 시간이 제공된 경우)
        if all([new_open_time, new_close_time, new_pickup_start_time, new_pickup_end_time]):
            if not self._validate_times(
                new_open_time, new_close_time, 
                new_pickup_start_time, new_pickup_end_time
            ):
                raise ValueError("시간 설정이 올바르지 않습니다.")
        
        # 부분 시간 검증 (일부만 변경하는 경우)
        elif any([new_open_time, new_close_time, new_pickup_start_time, new_pickup_end_time]):
            # 현재 값과 새 값을 조합하여 검증
            open_t = new_open_time or operation_info.open_time
            close_t = new_close_time or operation_info.close_time
            pickup_start = new_pickup_start_time or operation_info.pickup_start_time
            pickup_end = new_pickup_end_time or operation_info.pickup_end_time
            
            if not self._validate_times(open_t, close_t, pickup_start, pickup_end):
                raise ValueError("시간 설정이 올바르지 않습니다.")
        
        # 수정 예약 생성
        return await self.create(
            operation_id=operation_id,
            new_open_time=new_open_time,
            new_close_time=new_close_time,
            new_pickup_start_time=new_pickup_start_time,
            new_pickup_end_time=new_pickup_end_time,
            new_is_open_enabled=new_is_open_enabled
        )
    
    async def apply_modification(self, modification_id: int) -> bool:
        """수정 예약 적용"""
        modification = await self.get_by_pk(modification_id)
        if not modification:
            return False
        
        # 관련 운영 정보 조회
        operation_info = await self.session.get(StoreOperationInfo, modification.operation_id)
        if not operation_info:
            return False
        
        try:
            # 변경사항 적용
            if modification.new_open_time is not None:
                operation_info.open_time = modification.new_open_time
            if modification.new_close_time is not None:
                operation_info.close_time = modification.new_close_time
            if modification.new_pickup_start_time is not None:
                operation_info.pickup_start_time = modification.new_pickup_start_time
            if modification.new_pickup_end_time is not None:
                operation_info.pickup_end_time = modification.new_pickup_end_time
            if modification.new_is_open_enabled is not None:
                operation_info.is_open_enabled = modification.new_is_open_enabled
            
            # 수정 예약 삭제
            await self.delete(modification_id)
            
            await self.session.flush()
            return True
            
        except Exception as e:
            raise e
    
    async def apply_all_pending(self) -> List[int]:
        """대기 중인 모든 수정 예약 적용"""
        pending = await self.get_pending_modifications()
        applied_ids = []
        
        for modification in pending:
            try:
                if await self.apply_modification(modification.modification_id):
                    applied_ids.append(modification.modification_id)
                    logger.info(f"수정 예약 적용 성공: modification_id={modification.modification_id}")
            except Exception as e:
                # 개별 수정 실패는 건너뛰고 계속
                logger.error(
                    f"수정 예약 적용 실패: modification_id={modification.modification_id}, "
                    f"operation_id={modification.operation_id}, error={str(e)}"
                )
                continue
        
        logger.info(f"총 {len(applied_ids)}개의 수정 예약이 적용되었습니다.")
        return applied_ids
    
    async def cancel_modification(self, modification_id: int) -> bool:
        """수정 예약 취소"""
        return await self.delete(modification_id)
    
    async def update_modification(
        self,
        modification_id: int,
        new_open_time: Optional[time] = None,
        new_close_time: Optional[time] = None,
        new_pickup_start_time: Optional[time] = None,
        new_pickup_end_time: Optional[time] = None,
        new_is_open_enabled: Optional[bool] = None
    ) -> Optional[StoreOperationInfoModification]:
        """예약된 수정 정보 업데이트"""
        
        # 기존 수정 예약 조회
        modification = await self.get_by_pk(modification_id)
        if not modification:
            logger.warning(f"수정 예약을 찾을 수 없습니다: modification_id={modification_id}")
            return None
        
        # 관련 운영 정보 조회
        operation_info = await self.session.get(StoreOperationInfo, modification.operation_id)
        if not operation_info:
            logger.error(f"운영 정보를 찾을 수 없습니다: operation_id={modification.operation_id}")
            return None
        
        # 업데이트할 값 준비 (기존 예약값 우선, 없으면 현재 운영정보값)
        check_open = new_open_time if new_open_time is not None else (
            modification.new_open_time or operation_info.open_time
        )
        check_close = new_close_time if new_close_time is not None else (
            modification.new_close_time or operation_info.close_time
        )
        check_pickup_start = new_pickup_start_time if new_pickup_start_time is not None else (
            modification.new_pickup_start_time or operation_info.pickup_start_time
        )
        check_pickup_end = new_pickup_end_time if new_pickup_end_time is not None else (
            modification.new_pickup_end_time or operation_info.pickup_end_time
        )
        
        # 시간 유효성 검증
        if not self._validate_times(check_open, check_close, check_pickup_start, check_pickup_end):
            raise ValueError("시간 설정이 올바르지 않습니다.")
        
        # 업데이트할 데이터 준비
        update_data = {}
        
        # 값이 제공된 경우만 업데이트 (None 체크)
        if new_open_time is not None:
            update_data["new_open_time"] = new_open_time
        if new_close_time is not None:
            update_data["new_close_time"] = new_close_time
        if new_pickup_start_time is not None:
            update_data["new_pickup_start_time"] = new_pickup_start_time
        if new_pickup_end_time is not None:
            update_data["new_pickup_end_time"] = new_pickup_end_time
        if new_is_open_enabled is not None:
            update_data["new_is_open_enabled"] = new_is_open_enabled
        
        # 업데이트 실행
        if update_data:
            updated = await self.update(modification_id, **update_data)
            return updated
        
        return modification
    
    def _validate_times(
        self,
        open_time: time,
        close_time: time,
        pickup_start: time,
        pickup_end: time
    ) -> bool:
        """시간 유효성 검증"""
        # 오픈 시간 < 마감 시간
        if open_time >= close_time:
            return False
        
        # 픽업 시작 >= 오픈 시간 AND 픽업 시작 < 마감 시간
        if pickup_start < open_time or pickup_start >= close_time:
            return False
        
        # 픽업 종료 > 픽업 시작 AND 픽업 종료 <= 마감 시간
        if pickup_end <= pickup_start or pickup_end > close_time:
            return False
        
        return True