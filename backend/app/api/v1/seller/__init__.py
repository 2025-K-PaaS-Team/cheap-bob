from fastapi import APIRouter

from api.v1.seller import (
    store, 
    store_profile,
    store_settings,
    store_sns,
    store_images,
    product, 
    order
)

router = APIRouter(prefix="/seller")

router.include_router(store.router)
router.include_router(store_profile.router)
router.include_router(store_settings.router)
router.include_router(store_sns.router)
router.include_router(store_images.router)
router.include_router(product.router)
router.include_router(order.router)