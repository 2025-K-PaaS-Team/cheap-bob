from fastapi import APIRouter

from app.domain.customer.router import (
    favorite,
    history,
    option,
    preference,
    profile,
    register,
    search,
    withdraw,
)


customer_router = APIRouter(prefix="/customer", tags=["Customer"])
customer_router.include_router(register.router)
customer_router.include_router(profile.router)
customer_router.include_router(preference.router)
customer_router.include_router(withdraw.router)
customer_router.include_router(search.router)
customer_router.include_router(favorite.router)
customer_router.include_router(history.router)


# /common/options 는 customer 도메인 책임이지만 legacy 클라이언트와의 호환을 위해 /common 프리픽스를 유지한다.
common_router = APIRouter(prefix="/common", tags=["Common"])
common_router.include_router(option.router)
