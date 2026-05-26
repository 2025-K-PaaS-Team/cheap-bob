"""order 도메인의 internal API — payment-svc 가 호출.

핵심: create_order_from_cart 는 payment_id 멱등.
"""
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject

from app.middleware.internal_token import require_internal_token
from app.domain.order.repository.order_current_item import OrderCurrentItemRepository
from app.domain.order.dto.order import OrderStatus
from app.domain.customer.service.customer_profile import CustomerProfileService
from app.database.session import UnitOfWork, transactional


# ───────── schemas ─────────


class CreateOrderFromCartRequest(BaseModel):
    payment_id: str
    product_id: str
    customer_id: str
    quantity: int
    price: int
    sale: Optional[int] = None
    total_amount: int


# ───────── helper service (router 안에서만 사용. 짧으니 별도 service 파일 안 만듦) ─────────


class _CreateOrderHandler:
    """payment_id 멱등 + customer preference snapshot 캡처 + OrderCurrentItem INSERT.

    같은 tx 안에서 preference 조회 + order INSERT 를 묶는다. 
    preference 변경 race 는 payment-svc init 시점과 backend 의 finalize 시점 사이 customer 가 선호를 바꾸면 갱신된 값이 스냅샷에 들어간다 — 기존 single-process 흐름과 동일.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        customer_profile_service: CustomerProfileService,
    ):
        self.uow = uow
        self.customer_profile_service = customer_profile_service


    @transactional
    async def create(self, request: CreateOrderFromCartRequest) -> bool:
        """Returns True 면 새로 만든 것, False 면 멱등 no-op."""
        repo = OrderCurrentItemRepository(self._session)
        existing = await repo.get_by_pk(request.payment_id)
        if existing is not None:
            return False

        preference = await self.customer_profile_service.get_preference_snapshot(
            request.customer_id,
        )
        await repo.create(
            payment_id=request.payment_id,
            product_id=request.product_id,
            customer_id=request.customer_id,
            quantity=request.quantity,
            price=request.price,
            sale=request.sale,
            total_amount=request.total_amount,
            status=OrderStatus.reservation,
            reservation_at=datetime.now(timezone.utc),
            preferred_menus=preference.get("preferred_menus"),
            nutrition_types=preference.get("nutrition_types"),
            allergies=preference.get("allergies"),
            topping_types=preference.get("topping_types"),
        )
        return True


# ───────── router ─────────


internal_router = APIRouter(
    # 최종 등록 경로 = /api/internal (집계기) + /order = /api/internal/order/...
    prefix="/order",
    tags=["Internal/Order"],
    dependencies=[Depends(require_internal_token)],
)


@internal_router.post(
    "/orders/from-cart",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def create_order_from_cart(
    request: CreateOrderFromCartRequest,
    uow: UnitOfWork = Depends(Provide["uow"]),
    customer_profile_service: CustomerProfileService = Depends(
        Provide["customer_profile_service"],
    ),
):
    """payment-svc 의 finalize 가 호출. payment_id UNIQUE 멱등 — 두 번째 호출은 noop 으로 204."""
    handler = _CreateOrderHandler(
        uow=uow, customer_profile_service=customer_profile_service,
    )
    await handler.create(request)
