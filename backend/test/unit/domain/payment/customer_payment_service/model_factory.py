from datetime import datetime, time, timedelta, timezone
from types import SimpleNamespace
from typing import Optional


_KST = timezone(timedelta(hours=9))


class ProductFactory:
    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        product_id: str = "PRD_x",
        store_id: str = "STR_x",
        price: int = 10000,
        sale: Optional[int] = None,
        current_stock: int = 5,
    ) -> SimpleNamespace:
        cls._counter += 1
        return SimpleNamespace(
            product_id=product_id,
            store_id=store_id,
            price=price,
            sale=sale,
            current_stock=current_stock,
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0


class OperationInfoFactory:
    """``seller_store_read_service.get_today_operation`` 반환값.

    ``op.is_currently_open`` 과 ``op.pickup_end_time`` 만 서비스가 사용한다.
    """
    @classmethod
    def open(cls, *, pickup_end_time: Optional[time] = None) -> SimpleNamespace:
        return SimpleNamespace(
            is_currently_open=True,
            pickup_end_time=pickup_end_time or time(23, 59),
        )


    @classmethod
    def closed(cls) -> SimpleNamespace:
        return SimpleNamespace(
            is_currently_open=False,
            pickup_end_time=time(22, 0),
        )


    @classmethod
    def pickup_ended(cls) -> SimpleNamespace:
        return SimpleNamespace(
            is_currently_open=True,
            pickup_end_time=time(0, 1),  # KST 자정 직후 — 무조건 지난 시간
        )


class PaymentInfoFactory:
    @classmethod
    def create(
        cls,
        *,
        store_id: str = "STR_x",
        portone_store_id: str = "ps_x",
        portone_channel_id: str = "pc_x",
        portone_secret_key: str = "sk_x",
    ) -> SimpleNamespace:
        return SimpleNamespace(
            store_id=store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
            portone_secret_key=portone_secret_key,
        )


class CartItemFactory:
    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        payment_id: str = "PAY_x",
        product_id: str = "PRD_x",
        customer_id: str = "alice@example.com",
        quantity: int = 1,
        price: int = 10000,
        sale: Optional[int] = None,
        total_amount: int = 10000,
        expires_at: Optional[datetime] = None,
    ) -> SimpleNamespace:
        cls._counter += 1
        return SimpleNamespace(
            payment_id=payment_id,
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            price=price,
            sale=sale,
            total_amount=total_amount,
            expires_at=expires_at or (datetime.now(timezone.utc) + timedelta(minutes=5)),
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0
