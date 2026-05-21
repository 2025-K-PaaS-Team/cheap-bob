from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.domain.order.model.cart_item import CartItem
from app.database.postgresql_repository import BaseRepository


class CartItemRepository(BaseRepository[CartItem]):
    """장바구니 — 임시 재고 차감."""

    def __init__(self, session: AsyncSession):
        super().__init__(CartItem, session)


    async def get_by_payment_id(self, payment_id: str) -> Optional[CartItem]:
        return await self.get_by_pk(payment_id)


    async def lock_by_payment_id(self, payment_id: str) -> Optional[CartItem]:
        """`SELECT … FOR UPDATE` — confirm 와 sweeper 의 동시 finalize 직렬화.

        sweep_expired_carts 의 outer FOR UPDATE SKIP LOCKED 과 confirm_payment 의 본 lock
        이 같은 row 에 모이면 한쪽이 대기. 첫 흐름이 cart 를 DELETE + commit 하면 두번째
        흐름의 select 는 None 을 받아 NoOp (confirm 은 PaymentNotFoundError, sweep 은
        SKIP LOCKED 로 애초에 만나지 않음).
        """
        stmt = (
            select(CartItem)
            .where(CartItem.payment_id == payment_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def claim_expired_for_processing(
        self, *, now: datetime, limit: int,
    ) -> List[CartItem]:
        """만료된 cart_item 을 행 단위 락으로 선점. SKIP LOCKED 로 다른 노드의 동일 row 와 충돌 회피.

        sweeper worker 가 본 메서드로 batch 를 받아서 멱등하게 처리. 호출자 트랜잭션이
        commit 되기 전까지 다른 sweeper 가 같은 row 를 잡지 못한다.
        """
        stmt = (
            select(CartItem)
            .where(CartItem.expires_at <= now)
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())