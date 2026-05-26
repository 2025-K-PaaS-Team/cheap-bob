from fastapi import APIRouter

from app.domain.order.router import customer_order, seller_order


# 별도 prefix 없이 그대로 mount — 각 router 가 자체 prefix 를 가짐.
order_router = APIRouter(tags=["Order"])
order_router.include_router(customer_order.router)
order_router.include_router(seller_order.router)
