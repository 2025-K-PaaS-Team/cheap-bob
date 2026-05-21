"""SimpleNamespace 기반 도메인 객체 팩토리.

OrderCurrentItem 의 응답 변환 (`_customer_order_response`) 은 ``order.customer.detail.nickname``,
``order.product.store.store_name`` 같이 깊은 속성에 의존한다. SQLAlchemy 모델 인스턴스를
직접 만들면 backref 이벤트가 `_sa_instance_state` 를 요구해 실패하므로 SimpleNamespace 로
이 nested 구조를 흉내낸다.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Optional

from app.domain.order.dto.order import OrderStatus


_NOW = datetime(2026, 4, 20, 12, 0, 0, tzinfo=timezone.utc)


class CustomerDetailFactory:
    _counter = 0

    @classmethod
    def create(
        cls, *, nickname: str = "닉네임", phone_number: str = "010-0000-0000",
    ) -> SimpleNamespace:
        cls._counter += 1
        return SimpleNamespace(nickname=nickname, phone_number=phone_number)


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0


class CustomerFactory:
    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        email: str = "customer@example.com",
        detail: Optional[SimpleNamespace] = None,
    ) -> SimpleNamespace:
        cls._counter += 1
        return SimpleNamespace(
            email=email,
            detail=detail or CustomerDetailFactory.create(),
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0


class StoreFactory:
    """Store + today_operation_info 를 묶어 제공한다.

    customer_order 의 today 목록은 ``order.product.store.today_operation_info.pickup_start_time``
    같은 깊은 접근을 한다. operation_info 객체는 ``strftime("%H:%M")`` 호환의 ``.pickup_start_time``,
    ``.pickup_end_time`` 을 제공해야 한다.
    """
    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        store_id: str = "STR_test",
        store_name: str = "치킨집",
        with_today_operation: bool = False,
        pickup_start_time: Optional[datetime] = None,
        pickup_end_time: Optional[datetime] = None,
        images: Optional[list] = None,
    ) -> SimpleNamespace:
        cls._counter += 1
        today = None
        if with_today_operation:
            today = SimpleNamespace(
                pickup_start_time=pickup_start_time or datetime(2026, 4, 20, 18, 0),
                pickup_end_time=pickup_end_time or datetime(2026, 4, 20, 22, 0),
            )
        return SimpleNamespace(
            store_id=store_id,
            store_name=store_name,
            today_operation_info=today,
            images=images or [],
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0


class ProductFactory:
    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        product_id: str = "PRD_test",
        product_name: str = "치킨",
        store: Optional[SimpleNamespace] = None,
    ) -> SimpleNamespace:
        cls._counter += 1
        s = store or StoreFactory.create()
        return SimpleNamespace(
            product_id=product_id,
            product_name=product_name,
            store=s,
            store_id=s.store_id,
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0


class OrderFactory:
    """OrderCurrentItem 의 SimpleNamespace 흉내.

    응답 변환이 깊은 속성에 의존하므로 customer / product 를 함께 끼워 넣는다.
    """
    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        payment_id: Optional[str] = None,
        customer_id: str = "customer@example.com",
        product_id: Optional[str] = None,
        store_id: str = "STR_test",
        quantity: int = 1,
        price: int = 10000,
        sale: Optional[int] = None,
        total_amount: Optional[int] = None,
        status: OrderStatus = OrderStatus.reservation,
        reservation_at: Optional[datetime] = None,
        accepted_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        canceled_at: Optional[datetime] = None,
        cancel_reason: Optional[str] = None,
        preferred_menus: Optional[str] = None,
        nutrition_types: Optional[str] = None,
        allergies: Optional[str] = None,
        topping_types: Optional[str] = None,
        with_today_operation: bool = False,
        customer: Optional[SimpleNamespace] = None,
        product: Optional[SimpleNamespace] = None,
    ) -> SimpleNamespace:
        cls._counter += 1
        pid = payment_id or f"PAY_test_{cls._counter:04d}"
        prod_id = product_id or f"PRD_test_{cls._counter:04d}"
        amount = total_amount if total_amount is not None else price * quantity

        cust = customer or CustomerFactory.create(email=customer_id)
        prod = product or ProductFactory.create(
            product_id=prod_id,
            store=StoreFactory.create(
                store_id=store_id, with_today_operation=with_today_operation,
            ),
        )

        return SimpleNamespace(
            payment_id=pid,
            customer_id=customer_id,
            product_id=prod_id,
            quantity=quantity,
            price=price,
            sale=sale,
            total_amount=amount,
            status=status,
            reservation_at=reservation_at or _NOW,
            accepted_at=accepted_at,
            completed_at=completed_at,
            canceled_at=canceled_at,
            cancel_reason=cancel_reason,
            preferred_menus=preferred_menus,
            nutrition_types=nutrition_types,
            allergies=allergies,
            topping_types=topping_types,
            customer=cust,
            product=prod,
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0


class OrderHistoryFactory:
    """OrderHistoryItem (Mongo) 의 SimpleNamespace 흉내."""
    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        payment_id: Optional[str] = None,
        customer_id: str = "customer@example.com",
        product_id: str = "PRD_h",
        store_id: str = "STR_h",
        status: str = "complete",
    ) -> SimpleNamespace:
        cls._counter += 1
        pid = payment_id or f"PAY_h_{cls._counter:04d}"
        return SimpleNamespace(
            payment_id=pid,
            customer_id=customer_id,
            customer_nickname="이름",
            customer_phone_number="010",
            product_id=product_id,
            product_name="히스토리 치킨",
            store_id=store_id,
            store_name="히스토리 가게",
            quantity=1,
            price=10000,
            sale=None,
            total_amount=10000,
            status=status,
            reservation_at=_NOW,
            accepted_at=_NOW,
            completed_at=_NOW,
            canceled_at=None,
            cancel_reason=None,
            preferred_menus=None,
            nutrition_types=None,
            allergies=None,
            topping_types=None,
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0
