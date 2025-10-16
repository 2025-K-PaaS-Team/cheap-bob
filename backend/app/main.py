from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from api.v1.api import api_router
from config.settings import settings
from middleware.auth import JWTAuthMiddleware
from services.auth.jwt import JWTService
from database.mongodb_session import init_mongodb, close_mongodb
from services.scheduler import scheduler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("애플리케이션 시작 중...")
    await init_mongodb()
    scheduler.start()
    logger.info(f"스케줄러 상태: {'실행 중' if scheduler.is_running else '중지됨'}")
    yield
    # Shutdown
    logger.info("애플리케이션 종료 중...")
    scheduler.stop()
    await close_mongodb()


app = FastAPI(
    title="CheapBob API",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# JWT 인증 미들웨어 추가
jwt_service = JWTService()
app.add_middleware(JWTAuthMiddleware, jwt_service=jwt_service)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,    
        settings.FRONTEND_LOCAL_URL
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-New-Token"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}