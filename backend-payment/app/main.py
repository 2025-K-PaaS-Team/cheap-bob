import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager


# uvicorn 의 cwd 가 어디든 동작하도록 /backend-payment 만 sys.path 최상위.
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
        logger.info("payment-svc 시작 중...")
        scheduler.start()
        logger.info("스케줄러 상태: {}", "실행 중" if scheduler.is_running else "중지됨")

        yield

        logger.info("payment-svc 종료 중...")
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
        return {"status": "ok"}

    app.container = container
    return app


app = create_app()
