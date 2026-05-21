"""/api/v1 라우터 집계.

5개 도메인 (auth / customer / seller / order / payment)
"""

from fastapi import APIRouter

from app.domain.seller.router import seller_router
from app.domain.payment.router import payment_router
from app.domain.order.router import order_router
from app.domain.customer.router import common_router, customer_router
from app.domain.auth.router import auth_router, user_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(common_router)
api_router.include_router(customer_router)
api_router.include_router(seller_router)
api_router.include_router(order_router)
api_router.include_router(payment_router)
