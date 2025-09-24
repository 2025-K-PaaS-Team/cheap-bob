from fastapi import APIRouter

from api.v1.test import payment, mongodb

router = APIRouter(prefix="/test", tags=["Test"])

router.include_router(payment.router)
router.include_router(mongodb.router)