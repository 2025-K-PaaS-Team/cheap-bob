from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.config.settings import settings
from app.middleware.auth import JWTAuthMiddleware
from app.services.auth.jwt import JWTService

app = FastAPI(
    title="CheapBob API",
    version="0.1.0",
    debug=settings.DEBUG
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
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to CheapBob API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}