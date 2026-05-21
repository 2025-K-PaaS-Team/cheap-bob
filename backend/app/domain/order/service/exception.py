class OrderNotFoundError(Exception):
    """주문이 존재하지 않음."""


class OrderAlreadyCanceledError(Exception):
    """이미 취소된 주문."""


class OrderNotInReservationError(Exception):
    """예약 상태가 아닌 주문 (수락/완료/취소된 주문에 대한 잘못된 전이)."""


class OrderAlreadyCompletedError(Exception):
    """이미 픽업 완료."""


class OrderNotAcceptedError(Exception):
    """수락되지 않은 주문 (QR 발급/완료 시도 차단)."""


class OrderRefundError(Exception):
    """포트원 환불 실패."""


class OrderQrInvalidError(Exception):
    """QR 데이터가 잘못됨 (서명 위조 / 만료 등)."""


class OrderOwnershipMismatchError(Exception):
    """JWT/QR/주문 의 customer_id 또는 product_id 불일치."""


class OrderStockConflictError(Exception):
    """재고 복구 중 낙관적 락 충돌이 끝까지 해소되지 않음."""


class ProductStockReservationNotFoundError(Exception):
    """재고 예약이 없음."""
