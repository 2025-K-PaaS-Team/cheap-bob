class PaymentInfoMissingError(Exception):
    """가게의 결제 정보가 설정되지 않음."""


class PaymentInfoIncompleteError(Exception):
    """결제 정보의 일부 필드 (portone_*) 누락."""


class PaymentInfoAlreadyExistsError(Exception):
    """이미 등록된 결제 정보."""


class PaymentVerificationError(Exception):
    """PortOne 결제 검증 실패."""


class PaymentRefundError(Exception):
    """PortOne 환불 실패."""


class PaymentNotFoundError(Exception):
    """장바구니에 매칭되는 결제가 없음."""


class PaymentOwnershipMismatchError(Exception):
    """결제 소유자가 요청자와 다름."""


class PaymentTimeoutError(Exception):
    """결제 시간 만료 (5분 초과)."""


class ProductNotFoundError(Exception):
    """결제 대상 상품이 없음."""


class StoreNotOpenError(Exception):
    """가게가 영업 중이 아님."""


class PickupTimeEndedError(Exception):
    """픽업 시간이 종료됨."""


class StockInsufficientError(Exception):
    """재고 부족."""


class StockConflictError(Exception):
    """재고 변경 중 낙관적 락 충돌."""
