"""테스트 모델 — payment-backend 분리 후 자체 정의 (내부 entity + HTTP DTO)."""
from typing import Optional
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone


class ProductFactory:
    """internal_seller_client.find_product 가 반환하는 ProductResponse DTO 형태."""

    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        product_id: str = "PRD_x",
        store_id: str = "STR_x",
        product_name: str = "상품",
        price: int = 10000,
        sale: Optional[int] = None,
        current_stock: int = 5,
    ) -> SimpleNamespace:
        cls._counter += 1
        return SimpleNamespace(
            product_id=product_id,
            store_id=store_id,
            product_name=product_name,
            price=price,
            sale=sale,
            current_stock=current_stock,
        )


    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0


class OperationInfoFactory:
    """internal_seller_client.get_today_operation 의 TodayOperationResponse DTO 형태.

    pickup_*_time 은 HH:MM:SS 문자열 (HTTP wire format).
    """
    @classmethod
    def open(cls, *, pickup_end_time: str = "23:59:00") -> SimpleNamespace:
        return SimpleNamespace(
            operation_id=1,
            day_of_week=0,
            is_open_enabled=True,
            is_currently_open=True,
            pickup_start_time="10:00:00",
            pickup_end_time=pickup_end_time,
        )


    @classmethod
    def closed(cls) -> SimpleNamespace:
        return SimpleNamespace(
            operation_id=1,
            day_of_week=0,
            is_open_enabled=True,
            is_currently_open=False,
            pickup_start_time="10:00:00",
            pickup_end_time="22:00:00",
        )


    @classmethod
    def pickup_ended(cls) -> SimpleNamespace:
        # KST 자정 직후 — 모든 시간이 지난 것으로 비교됨.
        return SimpleNamespace(
            operation_id=1,
            day_of_week=0,
            is_open_enabled=True,
            is_currently_open=True,
            pickup_start_time="00:00:00",
            pickup_end_time="00:00:01",
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
