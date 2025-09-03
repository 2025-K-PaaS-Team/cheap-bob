from fastapi import APIRouter

from api.v1.seller import store, product, order

router = APIRouter(prefix="/seller")

router.include_router(store.router)
router.include_router(product.router)
router.include_router(order.router)