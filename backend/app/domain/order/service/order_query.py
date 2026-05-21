"""cross-domain read 진입점.

auth.RegistrationStatus / customer.Withdraw / seller.* 가 order 데이터를 봐야 할 때 모두
본 서비스를 거친다. 직접 repository import 를 금지하는 컨벤션 §18 의 진입점.
"""
from typing import Dict, List, Optional
import pytz
from datetime import date, datetime, timedelta
from collections import defaultdict

from app.domain.order.repository.order_history_item import OrderHistoryItemRepository
from app.domain.order.repository.order_current_item import (
    OrderCurrentItemRepository,
)
from app.domain.order.model.order_current_item import OrderCurrentItem
from app.domain.order.dto.order import OrderStatus
from app.database.session import UnitOfWork, transactional


_KST = pytz.timezone("Asia/Seoul")
_ACTIVE_STATUSES = (OrderStatus.reservation, OrderStatus.accept)


class OrderQueryService:

    def __init__(
        self,
        uow: UnitOfWork,
        history_repo: OrderHistoryItemRepository,
    ):
        self.uow = uow
        self.history_repo = history_repo


    # ───────── customer.Withdraw 용 ─────────


    @transactional
    async def has_active_orders_for_customer(self, customer_email: str) -> bool:
        """소비자가 진행 중인 (reservation/accept) 주문을 갖고 있는지."""
        orders = await OrderCurrentItemRepository(
            self._session,
        ).get_customer_active_orders(customer_email)
        return bool(orders)


    # ───────── seller.Close 용 ─────────


    @transactional
    async def list_store_current_orders(
        self, store_id: str,
    ) -> List[OrderCurrentItem]:
        return await OrderCurrentItemRepository(
            self._session,
        ).get_store_current_orders_with_relations(store_id)


    @transactional
    async def list_store_orders_with_relations(
        self, store_id: str,
    ) -> List[OrderCurrentItem]:
        return await OrderCurrentItemRepository(
            self._session,
        ).get_store_orders_with_relations(store_id)


    @transactional
    async def cancel_order(
        self, *, payment_id: str, cancel_reason: Optional[str] = None,
    ) -> int:
        return await OrderCurrentItemRepository(self._session).cancel_order(
            payment_id, cancel_reason,
        )


    # ───────── payment.Customer 용 (cart + order 트랜잭션 진입점) ─────────


    @transactional
    async def create_cart_item(
        self,
        *,
        payment_id: str,
        product_id: str,
        customer_id: str,
        quantity: int,
        price: int,
        sale: Optional[int],
        total_amount: int,
    ):
        from app.domain.order.repository.cart_item import CartItemRepository

        return await CartItemRepository(self._session).create(
            payment_id=payment_id,
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            price=price,
            sale=sale,
            total_amount=total_amount,
        )


    @transactional
    async def get_cart_item(self, payment_id: str):
        from app.domain.order.repository.cart_item import CartItemRepository

        return await CartItemRepository(self._session).get_by_payment_id(payment_id)


    @transactional
    async def delete_cart_item(self, payment_id: str) -> bool:
        from app.domain.order.repository.cart_item import CartItemRepository

        return await CartItemRepository(self._session).delete(payment_id)


    @transactional
    async def create_order_from_cart(
        self,
        *,
        cart_item,
        preference_snapshot: Dict[str, Optional[str]],
    ):
        """cart_item 에 customer preference 스냅샷을 결합해 OrderCurrentItem 생성."""
        from datetime import datetime, timezone

        return await OrderCurrentItemRepository(self._session).create(
            payment_id=cart_item.payment_id,
            product_id=cart_item.product_id,
            customer_id=cart_item.customer_id,
            quantity=cart_item.quantity,
            price=cart_item.price,
            sale=cart_item.sale,
            total_amount=cart_item.total_amount,
            status=OrderStatus.reservation,
            reservation_at=datetime.now(timezone.utc),
            preferred_menus=preference_snapshot.get("preferred_menus"),
            nutrition_types=preference_snapshot.get("nutrition_types"),
            allergies=preference_snapshot.get("allergies"),
            topping_types=preference_snapshot.get("topping_types"),
        )


    # ───────── seller.Dashboard 용 ─────────


    @transactional
    async def store_purchased_quantities(self, store_id: str) -> Dict[str, int]:
        """가게의 cancel 제외 product_id 별 구매 누계."""
        orders = await OrderCurrentItemRepository(
            self._session,
        ).get_by_store_id(store_id)
        out: Dict[str, int] = defaultdict(int)
        for order in orders:
            if order.status != OrderStatus.cancel:
                out[order.product_id] += order.quantity
        return out


    # ───────── 스케줄러 worker 용 ─────────


    @transactional
    async def migrate_finished_orders_to_history(self) -> int:
        """OrderCurrentItem 을 Mongo OrderHistoryItem 으로 이관 후 SQL 에서 삭제.

        Returns: 아카이브된 row 수.
        """
        repo = OrderCurrentItemRepository(self._session)
        all_orders = await repo.get_all_orders_with_relations()
        if not all_orders:
            return 0

        orders_data = []
        for order in all_orders:
            orders_data.append({
                "payment_id": order.payment_id,
                "customer_id": order.customer_id,
                "customer_nickname": order.customer.detail.nickname,
                "customer_phone_number": order.customer.detail.phone_number,
                "product_id": order.product_id,
                "product_name": order.product.product_name,
                "store_id": order.product.store_id,
                "store_name": order.product.store.store_name,
                "quantity": order.quantity,
                "price": order.price,
                "sale": order.sale,
                "total_amount": order.total_amount,
                "status": (
                    order.status.value if hasattr(order.status, "value")
                    else str(order.status)
                ),
                "reservation_at": order.reservation_at,
                "accepted_at": order.accepted_at,
                "completed_at": order.completed_at,
                "canceled_at": order.canceled_at,
                "cancel_reason": order.cancel_reason,
                "preferred_menus": order.preferred_menus,
                "nutrition_types": order.nutrition_types,
                "allergies": order.allergies,
                "topping_types": order.topping_types,
            })

        archived = await self.history_repo.bulk_archive_orders(orders_data)
        await repo.delete_all_items()
        return archived


    # ───────── seller.Settlement 용 ─────────


    @transactional
    async def daily_settlement(
        self, *, store_id: str, start_date: date, end_date: date,
    ) -> List[Dict]:
        today = datetime.now(_KST).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        start_kst = _KST.localize(datetime.combine(start_date, datetime.min.time()))
        end_kst = _KST.localize(datetime.combine(end_date, datetime.max.time()))
        start_utc = start_kst.astimezone(pytz.UTC)
        end_utc = end_kst.astimezone(pytz.UTC)

        all_orders: List[Dict] = []

        if end_date >= today.date():
            order_repo = OrderCurrentItemRepository(self._session)
            current_orders = await order_repo.get_store_orders_with_relations(store_id)
            for o in current_orders:
                if o.status not in (OrderStatus.complete, OrderStatus.cancel):
                    continue
                kst_date, kst_time = _order_time_by_status(o, o.status)
                all_orders.append({
                    "product_name": o.product.product_name,
                    "quantity": o.quantity,
                    "total_amount": o.total_amount,
                    "status": o.status,
                    "date": kst_date,
                    "time_at": kst_time,
                })

        if start_date < today.date():
            history_orders = await self.history_repo.get_store_history(
                store_id=store_id, start_date=start_utc, end_date=end_utc,
            )
            for o in history_orders:
                if o.status not in ("complete", "cancel"):
                    continue
                kst_date, kst_time = _order_time_by_status(o, o.status)
                all_orders.append({
                    "product_name": o.product_name,
                    "quantity": o.quantity,
                    "total_amount": o.total_amount,
                    "status": OrderStatus[o.status],
                    "date": kst_date,
                    "time_at": kst_time,
                })

        daily: Dict[str, List[Dict]] = defaultdict(list)
        for o in all_orders:
            daily[o["date"]].append(o)

        return [
            {
                "date": d,
                "items": sorted(daily[d], key=lambda x: x["time_at"], reverse=True),
            }
            for d in sorted(daily.keys(), reverse=True)
        ]


    @transactional
    async def weekly_revenue(self, store_id: str) -> int:
        today_kst = datetime.now(_KST)
        days_since_monday = today_kst.weekday()
        monday_kst = (today_kst - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        monday_utc = monday_kst.astimezone(pytz.UTC)

        total = 0
        order_repo = OrderCurrentItemRepository(self._session)
        current_orders = await order_repo.get_store_orders_with_relations(store_id)
        for o in current_orders:
            if o.status == OrderStatus.complete:
                total += o.total_amount

        if days_since_monday > 0:
            yesterday_end_utc = (today_kst - timedelta(days=1)).replace(
                hour=23, minute=59, second=59, microsecond=999999,
            ).astimezone(pytz.UTC)
            history_orders = await self.history_repo.get_store_history(
                store_id=store_id, start_date=monday_utc, end_date=yesterday_end_utc,
            )
            for o in history_orders:
                if o.status == "complete":
                    total += o.total_amount

        return total


def _order_time_by_status(order, status) -> tuple[str, str]:
    """OrderCurrentItem / OrderHistoryItem 의 상태별 시간을 KST 로 변환."""
    if isinstance(status, str):
        status = OrderStatus[status]
    if status == OrderStatus.complete:
        time_at = order.completed_at
    elif status == OrderStatus.cancel:
        time_at = order.canceled_at
    elif status == OrderStatus.accept:
        time_at = order.accepted_at
    else:
        time_at = order.reservation_at
    kst_time = time_at.astimezone(_KST)
    return kst_time.strftime("%Y-%m-%d"), kst_time.strftime("%H:%M")
