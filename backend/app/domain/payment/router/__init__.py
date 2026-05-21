from fastapi import APIRouter

from app.domain.payment.router import customer, seller_settings


payment_router = APIRouter(tags=["Payment"])
payment_router.include_router(customer.router)
payment_router.include_router(seller_settings.router)
