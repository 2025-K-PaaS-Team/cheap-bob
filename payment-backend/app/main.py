import asyncio
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager


# uvicorn 의 cwd 가 어디든 동작하도록 /payment-backend 만 sys.path 최상위.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


from app.scheduler.static import static_scheduler as scheduler
from app.middleware.auth import JWTAuthMiddleware
import app.database.model  # noqa: F401 — Base.metadata 채우기 위한 부수효과.
from app.core.logger import get_logger, setup_logging
from app.core.exceptions import register_domain_exception_handler
from app.container import container
from app.config.setting import settings
from app.api.v1.router import api_router as v1_router
from app.api.internal.router import internal_router


logger = get_logger("app.main")


_WIRED_MODULES = [
    "app.domain.payment.router.customer",
    "app.domain.payment.router.seller_settings",
    "app.domain.payment.router.internal",
]


def create_app() -> FastAPI:
    container.wire(modules=_WIRED_MODULES)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        setup_logging()
        logger.info("payment-backend 시작 중...")
        scheduler.start()
        logger.info("스케줄러 상태: {}", "실행 중" if scheduler.is_running else "중지됨")

        # Kafka / Outbox — producer 먼저, 그 다음 Relay / Consumer 백그라운드 태스크.
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

        logger.info("payment-backend 종료 중...")
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
        await container.portone_client().close()
        await container.internal_seller_client().close()
        await container.internal_order_client().close()

    app = FastAPI(
        title="CheapBob Payment Service",
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(JWTAuthMiddleware, jwt_service=container.jwt_service())

    cors_origins = [settings.FRONTEND_URL]
    if settings.ENVIRONMENT == "dev":
        cors_origins.append(settings.FRONTEND_LOCAL_URL)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    app.include_router(v1_router)
    app.include_router(internal_router)
    register_domain_exception_handler(app)

    @app.get("/health")
    async def health_check():
        # 외부 의존성 (main-backend, PortOne) breaker 상태 노출 — 운영 가시성.
        return {
            "status": "ok",
            "breakers": [
                container.internal_seller_client().breaker.snapshot(),
                container.internal_order_client().breaker.snapshot(),
                container.portone_client().breaker.snapshot(),
            ],
        }

    app.container = container
    return app


app = create_app()
