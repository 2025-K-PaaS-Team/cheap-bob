from app.core.exceptions import DomainError


class OrderNotFoundError(DomainError):
    """주문이 존재하지 않음."""
    status_code = 404


class OrderAlreadyCanceledError(DomainError):
    """이미 취소된 주문."""
    status_code = 400


class OrderNotInReservationError(DomainError):
    """예약 상태가 아닌 주문 (수락/완료/취소된 주문에 대한 잘못된 전이)."""
    status_code = 400


class OrderAlreadyCompletedError(DomainError):
    """이미 픽업 완료."""
    status_code = 400


class OrderNotAcceptedError(DomainError):
    """수락되지 않은 주문 (QR 발급/완료 시도 차단)."""
    status_code = 400


class OrderRefundError(DomainError):
    """포트원 환불 실패."""
    status_code = 500


class OrderQrInvalidError(DomainError):
    """QR 데이터가 잘못됨 (서명 위조 / 만료 등)."""
    status_code = 400


class OrderOwnershipMismatchError(DomainError):
    """JWT/QR/주문 의 customer_id 또는 product_id 불일치."""
    status_code = 403


class OrderStockConflictError(DomainError):
    """재고 복구 중 낙관적 락 충돌이 끝까지 해소되지 않음."""
    status_code = 409


class ProductStockReservationNotFoundError(DomainError):
    """재고 예약이 없음."""
    status_code = 404
