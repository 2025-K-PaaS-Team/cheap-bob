"""/api/v1 라우터 집계 — payment-svc 의 외부 (frontend) API."""

from fastapi import APIRouter

from app.domain.payment.router import payment_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(payment_router)
