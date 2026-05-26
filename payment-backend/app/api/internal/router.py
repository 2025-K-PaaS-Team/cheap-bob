"""/api/internal 라우터 집계 — payment-backend 의 service-to-service API.

X-Internal-Token 헤더로 인증되며, JWT 미들웨어에서는 EXCLUDE 됨.
"""

from fastapi import APIRouter

from app.domain.payment.router.internal import internal_router as payment_internal


internal_router = APIRouter(prefix="/api/internal")
internal_router.include_router(payment_internal)
