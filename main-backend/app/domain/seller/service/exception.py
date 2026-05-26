from app.core.exceptions import DomainError


class StoreNotFoundError(DomainError):
    """seller 의 가게 정보가 없음."""
    status_code = 404


class StoreAlreadyRegisteredError(DomainError):
    """이미 가게가 등록된 판매자."""
    status_code = 409


class StorePaymentMissingError(DomainError):
    """가게 마감 처리 시 포트원 secret_key 누락."""
    status_code = 400


class StoreImageDuplicateError(DomainError):
    """초기 이미지 등록 시 이미 이미지가 있음."""
    status_code = 409


class StoreImageNotFoundError(DomainError):
    """이미지 조회/삭제 시 대상 없음."""
    status_code = 404


class StoreImageMainDeleteError(DomainError):
    """대표 이미지는 삭제할 수 없음."""
    status_code = 400


class StoreOperationReservationNotFoundError(DomainError):
    """변경 예약 없음."""
    status_code = 404


class StoreSNSNotFoundError(DomainError):
    """등록된 SNS 정보 없음."""
    status_code = 404


class ProductNotFoundError(DomainError):
    """상품 없음."""
    status_code = 404


class ProductAlreadyRegisteredError(DomainError):
    """MVP 제한: 이미 상품 등록됨."""
    status_code = 409


class ProductStockReservationNotFoundError(DomainError):
    """재고 예약 정보 없음."""
    status_code = 404


class ProductNutritionDuplicateError(DomainError):
    """이미 등록된 영양 정보."""
    status_code = 409

    def __init__(self, duplicates: list):
        self.duplicates = duplicates
        super().__init__(f"중복: {duplicates}")


class ProductNutritionNotFoundError(DomainError):
    """삭제 대상 영양 정보 없음."""
    status_code = 404

    def __init__(self, missing: list):
        self.missing = missing
        super().__init__(f"존재하지 않음: {missing}")


class ProductStockConflictError(DomainError):
    """낙관적 락 충돌로 재고 변경 실패."""
    status_code = 409


class ProductStockInsufficientError(DomainError):
    """재고 부족 — 잘못된 요청. 낙관적 락 충돌 (409) 과 의미가 다르므로 400."""
    status_code = 400


class SellerNotFoundError(DomainError):
    """판매자 없음."""
    status_code = 404


class SellerAlreadyWithdrawnError(DomainError):
    """이미 탈퇴 처리됨."""
    status_code = 409


class SellerAlreadyActiveError(DomainError):
    """이미 활성 상태 — 탈퇴 취소 불가."""
    status_code = 409


class SellerStoreOpenError(DomainError):
    """가게 오픈 상태 → 탈퇴 불가."""
    status_code = 403


class SellerWithdrawalRecordNotFoundError(DomainError):
    """탈퇴 기록 없음."""
    status_code = 404
