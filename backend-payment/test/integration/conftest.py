"""payment-svc 통합 테스트 공통 설정.

실 PostgreSQL (payment-svc 전용 DB) 에 대고 서비스 → repository → DB 전체 흐름을 검증한다.

환경변수 ``POSTGRES_TEST_URL`` 이 설정돼 있어야 실행되며, 미설정 시 모든 통합 테스트는
자동 skip 한다. backend 와 별도 DB 인스턴스 — backend 의 ``POSTGRES_TEST_URL`` 과 같은
DB 를 가리키면 안 된다 (각 서비스의 Base.metadata 가 다른 테이블만 알기 때문에 같은 DB
를 공유하면 drop_all 이 상대 서비스 테이블을 못 본 채 한쪽만 청소되어 잔존 row 가 남는다).

예시 (docker-compose 의 postgres-payment 컨테이너 사용)::

    POSTGRES_TEST_URL="postgresql+asyncpg://cho:hyeonsang@localhost:5433/chohyeonsang_payment_test"

payment-svc 모델은 stores / sellers 등 backend 도메인 테이블에 FK 가 없으므로
seed_seller / seed_customer 같은 fixture 는 본 conftest 에 없다 — 테스트는 store_id /
product_id 를 단순 문자열로 다룬다.
"""
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
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
            "예: POSTGRES_TEST_URL='postgresql+asyncpg://cho:hyeonsang@localhost:5433/chohyeonsang_payment_test'",
            allow_module_level=False,
        )
    return url


@pytest_asyncio.fixture
async def engine():
    """매 테스트마다 새 엔진을 열고 테이블을 초기화.

    asyncpg + pytest-asyncio 1.x 에서 session-scope async fixture 는 event loop 격리 문제를
    일으키므로 function-scope 로 두고 ``NullPool`` 로 연결 재사용을 끊는다. 속도보다 신뢰성을
    우선한 선택 — backend conftest 와 동일 정책.
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
