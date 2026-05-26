"""Beanie Document 모델 등록 — ``init_beanie`` 에 넘길 모델 리스트.

``session.py`` (트랜잭션/세션 책임) 가 도메인 모델을 직접 알지 않도록 본 모듈에
의존성을 모은다. SQLAlchemy 의 ``app/database/model.py`` 와 동일한 패턴.

도메인 추가 시 본 리스트에 Document 모델을 등록한다.
"""
from app.domain.seller.model.seller_withdraw_reservation import (
    SellerWithdrawReservation,
)
from app.domain.order.model.product_stock_reservation import ProductStockReservation
from app.domain.order.model.order_history_item import OrderHistoryItem
from app.domain.customer.model.customer_withdraw_reservation import (
    CustomerWithdrawReservation,
)


DOCUMENT_MODELS = [
    OrderHistoryItem,
    ProductStockReservation,
    SellerWithdrawReservation,
    CustomerWithdrawReservation,
]
