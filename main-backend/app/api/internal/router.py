"""/api/internal 라우터 집계 — main-backend 의 service-to-service API.

X-Internal-Token 헤더로 인증되며, JWT 미들웨어에서 EXCLUDE.
"""

from fastapi import APIRouter

from app.domain.seller.router.internal import internal_router as seller_internal
from app.domain.order.router.internal import internal_router as order_internal


internal_router = APIRouter(prefix="/api/internal")
internal_router.include_router(seller_internal)
internal_router.include_router(order_internal)
