from fastapi import APIRouter

from api.v1.customer import payment, search, order, profile, register, history

router = APIRouter(prefix="/customer")

router.include_router(payment.router)
router.include_router(search.router)
router.include_router(order.router)
router.include_router(profile.router)
router.include_router(register.router)
router.include_router(history.router)