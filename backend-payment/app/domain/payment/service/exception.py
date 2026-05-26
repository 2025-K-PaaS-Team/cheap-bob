from app.core.exceptions import DomainError


class PaymentInfoMissingError(DomainError):
    """가게의 결제 정보가 설정되지 않음."""
    status_code = 400


class PaymentInfoIncompleteError(DomainError):
    """결제 정보의 일부 필드 (portone_*) 누락."""
    status_code = 400


class PaymentInfoAlreadyExistsError(DomainError):
    """이미 등록된 결제 정보."""
    status_code = 409


class PaymentVerificationError(DomainError):
    """PortOne 결제 검증 실패."""
    status_code = 400


class PaymentRefundError(DomainError):
    """PortOne 환불 실패."""
    status_code = 500


class PaymentNotFoundError(DomainError):
    """장바구니에 매칭되는 결제가 없음."""
    status_code = 404


class PaymentOwnershipMismatchError(DomainError):
    """결제 소유자가 요청자와 다름."""
    status_code = 403


class PaymentTimeoutError(DomainError):
    """결제 시간 만료 (5분 초과)."""
    status_code = 408


class ProductNotFoundError(DomainError):
    """결제 대상 상품이 없음."""
    status_code = 404


class StoreNotFoundError(DomainError):
    """backend 에서 seller_email → store_id 조회 시 가게가 없음."""
    status_code = 404


class StoreNotOpenError(DomainError):
    """가게가 영업 중이 아님."""
    status_code = 400


class PickupTimeEndedError(DomainError):
    """픽업 시간이 종료됨."""
    status_code = 400


class StockInsufficientError(DomainError):
    """재고 부족."""
    status_code = 400


class StockConflictError(DomainError):
    """재고 변경 중 낙관적 락 충돌."""
    status_code = 409


class BackendUnavailableError(DomainError):
    """backend 호출이 일시적으로 실패 — 5xx / 네트워크."""
    status_code = 502


class OrderCreateFailedError(DomainError):
    """backend 의 order 생성이 실패. finalize 보상 트리거."""
    status_code = 500
