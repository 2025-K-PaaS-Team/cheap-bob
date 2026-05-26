from typing import Generic, Optional, Type, TypeVar, List, Dict, Any, Union
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, asc, update

from app.database.session import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base Repository with generic CRUD operations"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        self._mapper = inspect(model)
        self._primary_key = self._get_primary_key()


    def _get_primary_key(self) -> str:
        pk_columns = self._mapper.primary_key
        if pk_columns:
            return pk_columns[0].name
        raise ValueError(f"No primary key found for {self.model.__name__}")


    async def create(self, **kwargs) -> ModelType:
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj


    async def get_by_pk(self, pk_value: Union[str, int]) -> Optional[ModelType]:
        pk_attr = getattr(self.model, self._primary_key)
        result = await self.session.execute(
            select(self.model).where(pk_attr == pk_value)
        )
        return result.scalar_one_or_none()


    async def get_one(self, **filters) -> Optional[ModelType]:
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
        query = select(self.model)

        if filters:
            query = self._build_filter_query(**filters)

        if load_relations:
            for relation in load_relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))

        if order_by:
            for order in order_by:
                if order.startswith('-'):
                    column = order[1:]
                    if hasattr(self.model, column):
                        query = query.order_by(desc(getattr(self.model, column)))
                else:
                    if hasattr(self.model, order):
                        query = query.order_by(asc(getattr(self.model, order)))

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()


    async def count(self, **filters) -> int:
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
        obj = await self.get_by_pk(pk_value)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            await self.session.flush()
            await self.session.refresh(obj)
        return obj


    async def update_where(self, filters: Dict[str, Any], **kwargs) -> int:
        query = self._build_filter_query(**filters)
        result = await self.session.execute(query)
        objects = result.scalars().all()

        for obj in objects:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

        await self.session.flush()
        return len(objects)


    async def update_lock(
        self,
        pk_value: Union[str, int],
        conditions: Dict[str, Any],
        **kwargs
    ) -> bool:
        pk_attr = getattr(self.model, self._primary_key)
        where_conditions = [pk_attr == pk_value]
        for key, value in conditions.items():
            if hasattr(self.model, key):
                where_conditions.append(getattr(self.model, key) == value)

        result = await self.session.execute(
            update(self.model)
            .where(and_(*where_conditions))
            .values(**kwargs)
        )
        await self.session.flush()
        return result.rowcount > 0


    async def delete(self, pk_value: Union[str, int]) -> bool:
        obj = await self.get_by_pk(pk_value)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
            return True
        return False


    async def delete_where(self, **filters) -> int:
        query = self._build_filter_query(**filters)
        result = await self.session.execute(query)
        objects = result.scalars().all()
        for obj in objects:
            await self.session.delete(obj)
        await self.session.flush()
        return len(objects)


    async def exists(self, **filters) -> bool:
        count = await self.count(**filters)
        return count > 0


    def _build_filter_query(self, **filters) -> Select:
        query = select(self.model)
        conditions = []

        for key, value in filters.items():
            if hasattr(self.model, key):
                if value is None:
                    conditions.append(getattr(self.model, key).is_(None))
                elif isinstance(value, list):
                    conditions.append(getattr(self.model, key).in_(value))
                else:
                    conditions.append(getattr(self.model, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        return query
