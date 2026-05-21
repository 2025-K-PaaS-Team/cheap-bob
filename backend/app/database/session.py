from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from functools import wraps
from contextvars import ContextVar
from beanie import init_beanie

from app.config.setting import settings


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 DeclarativeBase. 모든 ORM 모델의 부모."""


# 중첩 호출에서도 동일 트랜잭션을 공유하기 위한 세션 전파 채널.
_current_session: ContextVar = ContextVar("_current_session", default=None)


class UnitOfWork:
    """트랜잭션 경계를 관리하는 Unit of Work.

    `async with uow as session:` 진입 시 새 세션을 열고, 종료 시 예외 유무에 따라
    commit / rollback 한다.
    """

    def __init__(self, session: async_sessionmaker):
        self.session_factory = session


    async def __aenter__(self) -> AsyncSession:
        self.session = self.session_factory()
        return self.session


    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()


def transactional(fn):
    """진입점은 트랜잭션을 열고, 중첩 호출은 같은 세션에 참여시킨다.

    한 요청 안에서 여러 레포지토리가 한 트랜잭션으로 묶여야 일관성이 유지되며,
    중첩마다 새 세션을 열면 부분 commit 으로 데이터가 갈라질 위험이 있다.
    """
    @wraps(fn)
    async def wrapper(self, *args, **kwargs):
        existing = _current_session.get()
        if existing is not None:
            self._session = existing
            return await fn(self, *args, **kwargs)

        async with self.uow as session:
            token = _current_session.set(session)
            self._session = session
            try:
                return await fn(self, *args, **kwargs)
            finally:
                _current_session.reset(token)
                self._session = None
    return wrapper


class MongoDB:
    """MongoDB 클라이언트 + Beanie 초기화 래퍼."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None


    async def connect(self) -> None:
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.database = self.client[settings.MONGODB_NAME]

        # 도메인 추가 시 본 리스트에 Document 모델을 등록한다.
        # auth / customer / seller / order 모두 도메인 분리 완료.
        from app.domain.seller.model.seller_withdraw_reservation import (
            SellerWithdrawReservation,
        )
        from app.domain.order.model.product_stock_reservation import (
            ProductStockReservation,
        )
        from app.domain.order.model.order_history_item import OrderHistoryItem
        from app.domain.customer.model.customer_withdraw_reservation import (
            CustomerWithdrawReservation,
        )

        await init_beanie(
            database=self.database,
            document_models=[
                OrderHistoryItem,
                ProductStockReservation,
                SellerWithdrawReservation,
                CustomerWithdrawReservation,
            ],
        )


    async def disconnect(self) -> None:
        if self.client:
            self.client.close()


mongodb = MongoDB()


async def init_mongodb() -> None:
    await mongodb.connect()


async def close_mongodb() -> None:
    await mongodb.disconnect()
