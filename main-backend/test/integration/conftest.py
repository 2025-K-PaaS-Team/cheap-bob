"""통합 테스트 공통 설정.

실 PostgreSQL 에 대고 서비스 → repository → DB 전체 흐름을 검증한다.

환경변수 ``POSTGRES_TEST_URL`` 이 설정돼 있어야 실행되며, 미설정 시 모든 통합 테스트는
자동 skip 한다.

예시::

    POSTGRES_TEST_URL="postgresql+asyncpg://cho:hyeonsang@localhost:5432/chohyeonsang_test"
"""
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
import pytest_asyncio
import pytest
import os

from app.database.session import Base, UnitOfWork
import app.database.model  # noqa: F401 — Base.metadata 채우기


def _require_test_db_url() -> str:
    url = os.getenv("POSTGRES_TEST_URL")
    if not url:
        pytest.skip(
            "POSTGRES_TEST_URL 환경변수가 설정되지 않아 integration 테스트를 건너뜁니다. "
            "예: POSTGRES_TEST_URL='postgresql+asyncpg://cho:hyeonsang@localhost:5432/chohyeonsang_test'",
            allow_module_level=False,
        )
    return url


@pytest_asyncio.fixture
async def engine():
    """매 테스트마다 새 엔진을 열고 테이블을 초기화.

    asyncpg + pytest-asyncio 1.x 에서 session-scope async fixture 는 event loop 격리 문제를
    일으키므로 function-scope 로 두고 ``NullPool`` 로 연결 재사용을 끊는다. 속도보다 신뢰성을
    우선한 선택.
    """
    url = _require_test_db_url()
    engine = create_async_engine(url, echo=False, future=True, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def uow(session_factory) -> UnitOfWork:
    return UnitOfWork(session=session_factory)


@pytest_asyncio.fixture
async def seed_customer(session_factory):
    """원하는 개수만큼 Customer + CustomerDetail 을 심고 email 목록을 반환한다.

    OrderCurrentItem.customer 관계는 CustomerDetail 까지 selectinload 되므로, 두 row 를 함께
    심어야 응답 변환 (`_seller_response`) 에서 nickname/phone 이 None 이 아닌 실값이 된다.
    """
    from app.domain.customer.model.customer import Customer
    from app.domain.customer.model.customer_detail import CustomerDetail

    counter = {"value": 0}

    async def _seed(count: int = 1) -> list[str]:
        emails: list[str] = []
        async with session_factory() as session:
            for _ in range(count):
                idx = counter["value"]
                counter["value"] += 1
                email = f"customer_it_{idx:03d}@example.com"
                emails.append(email)
                session.add(Customer(email=email, is_active=True))
                session.add(
                    CustomerDetail(
                        customer_email=email,
                        nickname=f"닉네임{idx}",
                        # phone_number 는 String(11). 하이픈 없이 숫자 11자리로.
                        phone_number=f"0100000{idx:04d}",
                    ),
                )
            await session.commit()
        return emails

    return _seed


@pytest_asyncio.fixture
async def seed_seller(session_factory):
    """Seller row 만 심는다 — Store / Product 는 각 테스트가 필요시 직접 생성."""
    from app.domain.seller.model.seller import Seller

    counter = {"value": 0}

    async def _seed(count: int = 1) -> list[str]:
        emails: list[str] = []
        async with session_factory() as session:
            for _ in range(count):
                idx = counter["value"]
                counter["value"] += 1
                email = f"seller_it_{idx:03d}@example.com"
                emails.append(email)
                session.add(Seller(email=email, is_active=True))
            await session.commit()
        return emails

    return _seed
