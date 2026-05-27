import asyncio
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager


# uvicorn 의 cwd 가 어디든 동작하도록 /main-backend 만 sys.path 최상위에 둔다.
# /main-backend/app 을 추가하면 같은 .py 파일이 `database.session` 과 `app.database.session` 두 모듈명으로 동시에 로드돼 SQLAlchemy MetaData 가 중복 등록되는 사고가 발생한다.
_ROOT = Path(__file__).resolve().parent.parent  # /main-backend
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


from app.scheduler.static import static_scheduler as scheduler
from app.scheduler.dynamic import DynamicScheduler
from app.middleware.auth import JWTAuthMiddleware
from app.database.session import close_mongodb, init_mongodb
import app.database.model  # noqa: F401 — Base.metadata 채우기 위한 부수효과 import.
from app.core.logger import get_logger, setup_logging
from app.core.exceptions import register_domain_exception_handler
from app.container import container
from app.config.setting import settings
from app.api.v1.router import api_router
from app.api.internal.router import internal_router


logger = get_logger("app.main")


# `@inject` 데코레이터를 쓰는 라우터 모듈만 wire 에 추가한다. 그 외 service / 일반 모듈은 불필요.
# payment 도메인은 MSA 분리 — payment-backend 에 wire.
_WIRED_MODULES = [
    "app.domain.auth.router.callback",
    "app.domain.auth.router.role",
    "app.domain.customer.router.register",
    "app.domain.customer.router.profile",
    "app.domain.customer.router.preference",
    "app.domain.customer.router.withdraw",
    "app.domain.customer.router.search",
    "app.domain.customer.router.favorite",
    "app.domain.customer.router.history",
    "app.domain.customer.router.option",
    "app.domain.seller.router.register",
    "app.domain.seller.router.store",
    "app.domain.seller.router.profile",
    "app.domain.seller.router.settings",
    "app.domain.seller.router.sns",
    "app.domain.seller.router.image",
    "app.domain.seller.router.product",
    "app.domain.seller.router.settlement",
    "app.domain.seller.router.withdraw",
    "app.domain.seller.router.internal",
    "app.domain.order.router.customer_order",
    "app.domain.order.router.seller_order",
    "app.domain.order.router.internal",
]


def create_app() -> FastAPI:
    container.wire(modules=_WIRED_MODULES)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        setup_logging()
        logger.info("애플리케이션 시작 중...")
        await init_mongodb()
        scheduler.start()
        logger.info("스케줄러 상태: {}", "실행 중" if scheduler.is_running else "중지됨")

        try:
            recovered = await DynamicScheduler.recover_if_needed(scheduler)
            if recovered:
                logger.info("서버 재시작으로 인한 동적 스케줄 복원 완료")
            else:
                logger.info("동적 스케줄 복원이 필요하지 않습니다")
        except Exception:
            logger.exception("동적 스케줄 복원 중 오류 발생")

        # Kafka / Outbox — producer 먼저 start (Relay 가 send 시 필요), Relay 와 Consumer 는
        # 백그라운드 태스크.
        kafka_producer = container.kafka_producer()
        outbox_relay = container.outbox_relay()
        consumer_runner = container.kafka_consumer_runner()

        await kafka_producer.start()
        relay_task = asyncio.create_task(outbox_relay.run())
        consumer_task = (
            asyncio.create_task(consumer_runner.run())
            if consumer_runner.topics() else None
        )

        yield

        logger.info("애플리케이션 종료 중...")
        # 종료 순서: 컨슈머 → Relay → Producer. Relay 가 in-flight send 를 끝낸 뒤
        # producer.stop 이 와야 메시지 손실이 없다.
        if consumer_task is not None:
            consumer_runner.request_stop()
            try:
                await asyncio.wait_for(consumer_task, timeout=5)
            except asyncio.TimeoutError:
                consumer_task.cancel()

        outbox_relay.request_stop()
        try:
            await asyncio.wait_for(relay_task, timeout=5)
        except asyncio.TimeoutError:
            relay_task.cancel()

        await kafka_producer.stop()
        scheduler.stop()
        await container.internal_payment_client().close()
        await close_mongodb()

    app = FastAPI(
        title="CheapBob API",
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # 인증 미들웨어 — Container 의 jwt_service Singleton 을 주입한다.
    app.add_middleware(JWTAuthMiddleware, jwt_service=container.jwt_service())

    # CORS — 등록 순서상 가장 마지막 (= 가장 바깥) 이라 모든 응답에 헤더가 붙는다.
    cors_origins = [settings.FRONTEND_URL]
    if settings.ENVIRONMENT == "dev":
        cors_origins.append(settings.FRONTEND_LOCAL_URL)
    # ``allow_credentials=True`` 와 wildcard 조합은 보안 표면을 넓힘 — 실제 사용 method/header
    # 만 명시한다. Authorization 은 dev 한정 헤더 토큰, Content-Type 은 일반 JSON/multipart,
    # X-Requested-With 는 일부 클라이언트의 AJAX 표시용.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    app.include_router(api_router)
    app.include_router(internal_router)
    register_domain_exception_handler(app)

    @app.get("/health")
    async def health_check():
        # 외부 의존성 breaker 상태 + outbox lag 를 함께 노출 — 운영 알람 룰의 입력.
        breaker_snapshot = container.internal_payment_client().breaker.snapshot()
        return {
            "status": "ok",
            "breakers": [breaker_snapshot],
        }

    app.container = container
    return app


app = create_app()
