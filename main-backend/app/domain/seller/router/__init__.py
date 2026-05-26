from fastapi import APIRouter

from app.domain.seller.router import (
    image,
    product,
    profile,
    register,
    settings,
    settlement,
    sns,
    store,
    withdraw,
)


seller_router = APIRouter(prefix="/seller", tags=["Seller"])
seller_router.include_router(register.router)
seller_router.include_router(store.router)
seller_router.include_router(profile.router)
seller_router.include_router(settings.router)
seller_router.include_router(sns.router)
seller_router.include_router(image.router)
seller_router.include_router(product.router)
seller_router.include_router(settlement.router)
seller_router.include_router(withdraw.router)
