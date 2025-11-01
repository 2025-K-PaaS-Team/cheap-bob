from fastapi import APIRouter

from api.v1.test import payment, email, qr_callback

router = APIRouter(prefix="/test", tags=["Test"])

router.include_router(payment.router)
router.include_router(email.router)
router.include_router(qr_callback.router)