from typing import List, Optional, Dict
from datetime import time, datetime, timezone, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
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
    
    async def create_modifications_batch(
        self,
        store_id: str,
        modifications_data: List[Dict]
    ) -> List[StoreOperationInfoModification]:
        """
        모든 요일의 운영 정보 변경 예약을 하나의 트랜잭션으로 생성
        
        Args:
            store_id: 가게 ID
            modifications_data: 요일별 변경 데이터 리스트
                [{
                    'day_of_week': 0,
                    'open_time': time(9, 0),
                    'close_time': time(22, 0),
                    'pickup_start_time': time(9, 30),
                    'pickup_end_time': time(21, 30),
                    'is_open_enabled': True
                }, ...]
        """
        operation_query = (
            select(StoreOperationInfo)
            .where(StoreOperationInfo.store_id == store_id)
        )
        result = await self.session.execute(operation_query)
        operation_infos = result.scalars().all()
        
        if not operation_infos or len(operation_infos) != 7:
            raise ValueError("가게 운영 정보가 올바르게 설정되어 있지 않습니다")
        
        operation_map = {info.day_of_week: info for info in operation_infos}
        
        existing_mods = await self.get_by_store_id(store_id)
        if existing_mods:
            raise ValueError("이미 운영 정보 변경 예약이 존재합니다")
        
        created_modifications = []
        
        try:
            for mod_data in modifications_data:
                day_of_week = mod_data['day_of_week']
                operation_info = operation_map.get(day_of_week)
                
                if not operation_info:
                    raise ValueError(f"요일 {day_of_week}에 대한 운영 정보를 찾을 수 없습니다")
                
                modification = StoreOperationInfoModification(
                    operation_id=operation_info.operation_id,
                    new_open_time=mod_data['open_time'],
                    new_close_time=mod_data['close_time'],
                    new_pickup_start_time=mod_data['pickup_start_time'],
                    new_pickup_end_time=mod_data['pickup_end_time'],
                    new_is_open_enabled=mod_data['is_open_enabled']
                )
                
                self.session.add(modification)
                created_modifications.append(modification)
            
            # 모든 변경사항을 단일 트랜잭션
            await self.session.flush()
            
            for mod in created_modifications:
                await self.session.refresh(mod, ['operation_info'])
            
            return created_modifications
            
        except Exception as e:
            raise e
    
    async def update_modifications_batch(
        self,
        store_id: str,
        modifications_data: List[Dict]
    ) -> List[StoreOperationInfoModification]:
        """
        모든 요일의 운영 정보 변경 예약을 하나의 트랜잭션으로 수정
        """
        existing_mods = await self.get_by_store_id(store_id)
        if not existing_mods:
            raise ValueError("운영 정보 변경 예약을 찾을 수 없습니다")
        
        existing_map = {mod.operation_info.day_of_week: mod for mod in existing_mods}
        
        operation_query = (
            select(StoreOperationInfo)
            .where(StoreOperationInfo.store_id == store_id)
        )
        result = await self.session.execute(operation_query)
        operation_infos = result.scalars().all()
        operation_map = {info.day_of_week: info for info in operation_infos}
        
        updated_modifications = []
        
        try:
            for mod_data in modifications_data:
                day_of_week = mod_data['day_of_week']
                operation_info = operation_map.get(day_of_week)
                
                if not operation_info:
                    raise ValueError(f"요일 {day_of_week}에 대한 운영 정보를 찾을 수 없습니다")
                
                existing_mod = existing_map.get(day_of_week)
                
                if existing_mod:
                    existing_mod.new_open_time = mod_data['open_time']
                    existing_mod.new_close_time = mod_data['close_time']
                    existing_mod.new_pickup_start_time = mod_data['pickup_start_time']
                    existing_mod.new_pickup_end_time = mod_data['pickup_end_time']
                    existing_mod.new_is_open_enabled = mod_data['is_open_enabled']
                    
                    updated_modifications.append(existing_mod)
                else:
                    new_mod = StoreOperationInfoModification(
                        operation_id=operation_info.operation_id,
                        new_open_time=mod_data['open_time'],
                        new_close_time=mod_data['close_time'],
                        new_pickup_start_time=mod_data['pickup_start_time'],
                        new_pickup_end_time=mod_data['pickup_end_time'],
                        new_is_open_enabled=mod_data['is_open_enabled']
                    )
                    
                    self.session.add(new_mod)
                    updated_modifications.append(new_mod)
            
            # 모든 변경사항을 단일 트랜잭션
            await self.session.flush()
            
            for mod in updated_modifications:
                if not hasattr(mod, 'operation_info') or not mod.operation_info:
                    await self.session.refresh(mod, ['operation_info'])
            
            return sorted(updated_modifications, key=lambda x: x.operation_info.day_of_week)
            
        except Exception as e:
            raise e
    
    async def delete_all_by_store_id(self, store_id: str) -> int:
        """
        가게의 모든 운영 정보 변경 예약을 하나의 트랜잭션으로 삭제
        
        Returns:
            삭제된 예약 개수
        """
        existing_mods = await self.get_by_store_id(store_id)
        if not existing_mods:
            raise ValueError("운영 정보 변경 예약을 찾을 수 없습니다")
        
        delete_count = len(existing_mods)
        
        try:
            delete_query = (
                delete(StoreOperationInfoModification)
                .where(
                    StoreOperationInfoModification.operation_id.in_(
                        select(StoreOperationInfo.operation_id)
                        .where(StoreOperationInfo.store_id == store_id)
                    )
                )
            )
            
            await self.session.execute(delete_query)
            await self.session.flush()
            
            return delete_count
            
        except Exception as e:
            raise e