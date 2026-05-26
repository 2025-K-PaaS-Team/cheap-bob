"""cart_items CRUD — payment-svc 내부 DB.

기존 backend.OrderQueryService 의 cart 관련 메서드들을 본 서비스로 분리.
sweep/lock 등 동시성 의미 유지 — 모두 같은 payment-svc tx 안에서 작동.
"""
from typing import List, Optional
from datetime import datetime

from app.domain.payment.repository.cart_item import CartItemRepository
from app.domain.payment.model.cart_item import CartItem
from app.database.session import UnitOfWork, transactional


class CartItemService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def create(
        self,
        *,
        payment_id: str,
        product_id: str,
        customer_id: str,
        quantity: int,
        price: int,
        sale: Optional[int],
        total_amount: int,
        expires_at: datetime,
    ) -> CartItem:
        return await CartItemRepository(self._session).create(
            payment_id=payment_id,
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            price=price,
            sale=sale,
            total_amount=total_amount,
            expires_at=expires_at,
        )


    @transactional
    async def get(self, payment_id: str) -> Optional[CartItem]:
        return await CartItemRepository(self._session).get_by_payment_id(payment_id)


    @transactional
    async def lock(self, payment_id: str) -> Optional[CartItem]:
        """SELECT … FOR UPDATE — confirm/sweep finalize race-safe 진입점."""
        return await CartItemRepository(self._session).lock_by_payment_id(payment_id)


    @transactional
    async def delete(self, payment_id: str) -> bool:
        return await CartItemRepository(self._session).delete(payment_id)


    @transactional
    async def claim_expired_for_processing(
        self, *, now: datetime, limit: int,
    ) -> List[CartItem]:
        """SKIP LOCKED 로 만료된 cart batch 를 선점 — sweeper 진입점."""
        return await CartItemRepository(
            self._session,
        ).claim_expired_for_processing(now=now, limit=limit)
