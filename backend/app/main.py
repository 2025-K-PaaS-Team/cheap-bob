from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import api_router
from config.settings import settings
from middleware.auth import JWTAuthMiddleware
from services.auth.jwt import JWTService
from database.mongodb_session import init_mongodb, close_mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_mongodb()
    yield
    # Shutdown
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