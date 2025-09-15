from typing import List, Optional, Dict
from datetime import time, datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.store_operation_info import StoreOperationInfo
from repositories.base import BaseRepository

# KST 타임존 설정
KST = timezone(timedelta(hours=9))


class StoreOperationInfoRepository(BaseRepository[StoreOperationInfo]):
    """가게 운영 정보 Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(StoreOperationInfo, session)
    
    async def get_by_store_id(self, store_id: str) -> List[StoreOperationInfo]:
        """가게 ID로 모든 요일의 운영 정보 조회"""
        return await self.get_many(
            filters={"store_id": store_id},
            order_by=["day_of_week"]
        )
    
    async def get_by_store_and_day(self, store_id: str, day_of_week: int) -> Optional[StoreOperationInfo]:
        """가게 ID와 요일로 운영 정보 조회"""
        return await self.get_one(
            store_id=store_id,
            day_of_week=day_of_week
        )
    
    async def create_initial_operation_info(
        self,
        store_id: str,
        operation_times: List[Dict]
    ) -> List[StoreOperationInfo]:
        """가게의 초기 운영 정보 생성 (스키마 기반)"""
        
        # 이미 운영 정보가 있는지 확인
        existing = await self.get_by_store_id(store_id)
        if existing:
            raise ValueError("이미 운영 정보가 등록되어 있습니다.")
        
        created_info = []
        
        try:
            # 전달받은 운영 시간 정보로 생성
            for op_time in operation_times:
                operation_info = await self.create(
                    store_id=store_id,
                    day_of_week=op_time['day_of_week'],
                    open_time=op_time['open_time'],
                    close_time=op_time['close_time'],
                    pickup_start_time=op_time['pickup_start_time'],
                    pickup_end_time=op_time['pickup_end_time'],
                    is_open_enabled=op_time['is_open_enabled'],
                    is_currently_open=False
                )
                created_info.append(operation_info)
            
            await self.session.commit()
            
            # 생성된 정보들 새로고침
            for info in created_info:
                await self.session.refresh(info)
            
            return created_info
            
        except Exception as e:
            await self.session.rollback()
            raise e
    
    async def update_open_status(
        self,
        operation_id: int,
        is_open_enabled: Optional[bool] = None,
        is_currently_open: Optional[bool] = None
    ) -> Optional[StoreOperationInfo]:
        """운영 상태 업데이트"""
        update_data = {}
        
        if is_open_enabled is not None:
            update_data["is_open_enabled"] = is_open_enabled
        if is_currently_open is not None:
            update_data["is_currently_open"] = is_currently_open
        
        if update_data:
            return await self.update(operation_id, **update_data)
        
        return await self.get_by_pk(operation_id)
    
    async def update_current_status_by_time(self, store_id: str) -> List[StoreOperationInfo]:
        """현재 날짜 운영 상태 업데이트(트리거)"""
        operation_infos = await self.get_by_store_id(store_id)
        
        now = datetime.now(KST)
        current_day = now.weekday()  # 0: Monday, 6: Sunday
        
        updated_infos = []
        
        for info in operation_infos:
            should_be_open = False
            
            # 해당 요일이고, 운영이 활성화되어 있는 경우
            if (info.day_of_week == current_day and 
                info.is_open_enabled):
                should_be_open = True
            
            # 상태가 변경되어야 하는 경우만 업데이트
            if info.is_currently_open != should_be_open:
                updated = await self.update_open_status(
                    info.operation_id,
                    is_currently_open=should_be_open
                )
                if updated:
                    updated_infos.append(updated)
        
        return updated_infos
    
    async def get_today_operation_info(self, store_id: str) -> Optional[StoreOperationInfo]:
        """오늘의 운영 정보 조회"""
        today = datetime.now(KST).weekday()
        return await self.get_by_store_and_day(store_id, today)
    
    async def is_pickup_available_now(self, store_id: str) -> bool:
        """현재 픽업 가능 여부 확인"""
        today_info = await self.get_today_operation_info(store_id)
        
        if not today_info or not today_info.is_open_enabled:
            return False
        
        current_time = datetime.now().time()
        return (today_info.pickup_start_time <= current_time <= today_info.pickup_end_time)
    
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