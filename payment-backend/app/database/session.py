from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from functools import wraps
from contextvars import ContextVar


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 DeclarativeBase. payment-backend 의 모든 ORM 모델의 부모."""


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
    """진입점은 트랜잭션을 열고, 중첩 호출은 같은 세션에 참여시킨다."""
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
