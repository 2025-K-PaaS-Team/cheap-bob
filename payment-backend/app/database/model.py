"""Alembic 자동 감지용 모델 집계.

`migration/env.py` 가 이 모듈만 import 하면 `Base.metadata` 에 payment-backend 의 모든 ORM
모델이 등록된다.
"""

from app.domain.payment.model.store_payment_info import StorePaymentInfo
from app.domain.payment.model.cart_item import CartItem


__all__ = [
    "StorePaymentInfo",
    "CartItem",
]
