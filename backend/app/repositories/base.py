from abc import ABC
from typing import Generic, Optional, Type, TypeVar, List, Dict, Any, Union
from sqlalchemy import select, func, and_, or_, desc, asc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select
from sqlalchemy.inspection import inspect

from database.session import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base Repository with generic CRUD operations"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        self._mapper = inspect(model)
        self._primary_key = self._get_primary_key()
    
    def _get_primary_key(self) -> str:
        """모델의 primary key 컬럼 이름을 자동으로 찾기"""
        pk_columns = self._mapper.primary_key
        if pk_columns:
            return pk_columns[0].name
        raise ValueError(f"No primary key found for {self.model.__name__}")
    
    async def create(self, **kwargs) -> ModelType:
        """새 레코드 생성"""
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def get_by_pk(self, pk_value: Union[str, int]) -> Optional[ModelType]:
        """Primary key로 조회 (타입에 관계없이)"""
        pk_attr = getattr(self.model, self._primary_key)
        result = await self.session.execute(
            select(self.model).where(pk_attr == pk_value)
        )
        return result.scalar_one_or_none()
    
    async def get_one(self, **filters) -> Optional[ModelType]:
        """필터 조건으로 단일 레코드 조회"""
        query = self._build_filter_query(**filters)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_many(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        load_relations: Optional[List[str]] = None
    ) -> List[ModelType]:
        """필터, 정렬, 페이지네이션을 지원하는 다중 레코드 조회"""
        query = select(self.model)
        
        # 필터 적용
        if filters:
            query = self._build_filter_query(**filters)
        
        # 관계 로딩
        if load_relations:
            for relation in load_relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))
        
        # 정렬
        if order_by:
            for order in order_by:
                if order.startswith('-'):
                    column = order[1:]
                    if hasattr(self.model, column):
                        query = query.order_by(desc(getattr(self.model, column)))
                else:
                    if hasattr(self.model, order):
                        query = query.order_by(asc(getattr(self.model, order)))
        
        # 페이지네이션
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count(self, **filters) -> int:
        """조건에 맞는 레코드 수 조회"""
        query = select(func.count()).select_from(self.model)
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def update(self, pk_value: Union[str, int], **kwargs) -> Optional[ModelType]:
        """Primary key로 레코드 업데이트"""
        obj = await self.get_by_pk(pk_value)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            await self.session.commit()
            await self.session.refresh(obj)
        return obj
    
    async def update_where(self, filters: Dict[str, Any], **kwargs) -> int:
        """조건에 맞는 여러 레코드 업데이트"""
        query = self._build_filter_query(**filters)
        result = await self.session.execute(query)
        objects = result.scalars().all()
        
        for obj in objects:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
        
        await self.session.commit()
        return len(objects)
    
    async def update_lock(
        self, 
        pk_value: Union[str, int],
        conditions: Dict[str, Any],
        **kwargs
    ) -> bool:
        """조건을 만족할 때만 업데이트 (낙관적 락 사용)"""
        pk_attr = getattr(self.model, self._primary_key)
        
        # WHERE 조건 구성
        where_conditions = [pk_attr == pk_value]
        
        # 추가 조건들
        for key, value in conditions.items():
            if hasattr(self.model, key):
                where_conditions.append(getattr(self.model, key) == value)
        
        # UPDATE 쿼리 실행
        result = await self.session.execute(
            update(self.model)
            .where(and_(*where_conditions))
            .values(**kwargs)
        )
        
        await self.session.commit()
        
        # rowcount로 성공 여부 반환
        return result.rowcount > 0
    
    async def delete(self, pk_value: Union[str, int]) -> bool:
        """Primary key로 레코드 삭제"""
        obj = await self.get_by_pk(pk_value)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False
    
    async def delete_and_return(self, pk_value: Union[str, int]) -> Optional[ModelType]:
        """레코드 삭제 후 삭제된 객체 반환"""
        obj = await self.get_by_pk(pk_value)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return obj
        return None
    
    async def delete_all_and_return(self) -> List[ModelType]:
        """모든 레코드 삭제 후 삭제된 객체들 반환"""
        # 모든 객체 조회
        result = await self.session.execute(select(self.model))
        objects = result.scalars().all()
        
        # 객체들을 메모리에 저장
        deleted_objects = list(objects)
        
        # 모두 삭제
        for obj in objects:
            await self.session.delete(obj)
        
        await self.session.commit()
        
        return deleted_objects
        
    async def delete_where(self, **filters) -> int:
        """조건에 맞는 여러 레코드 삭제"""
        query = self._build_filter_query(**filters)
        result = await self.session.execute(query)
        objects = result.scalars().all()
        
        for obj in objects:
            await self.session.delete(obj)
        
        await self.session.commit()
        return len(objects)
    
    async def exists(self, **filters) -> bool:
        """조건에 맞는 레코드 존재 여부 확인"""
        count = await self.count(**filters)
        return count > 0
    
    def _build_filter_query(self, **filters) -> Select:
        """필터 조건으로 쿼리 생성"""
        query = select(self.model)
        conditions = []
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                if value is None:
                    conditions.append(getattr(self.model, key).is_(None))
                elif isinstance(value, list):
                    conditions.append(getattr(self.model, key).in_(value))
                elif isinstance(value, dict):
                    # 고급 필터링: {"gt": 10, "lt": 20}
                    column = getattr(self.model, key)
                    if "gt" in value:
                        conditions.append(column > value["gt"])
                    if "gte" in value:
                        conditions.append(column >= value["gte"])
                    if "lt" in value:
                        conditions.append(column < value["lt"])
                    if "lte" in value:
                        conditions.append(column <= value["lte"])
                    if "like" in value:
                        conditions.append(column.like(f"%{value['like']}%"))
                    if "not" in value:
                        conditions.append(column != value["not"])
                else:
                    conditions.append(getattr(self.model, key) == value)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return query