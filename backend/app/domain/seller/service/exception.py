class StoreNotFoundError(Exception):
    """seller 의 가게 정보가 없음."""


class StoreAlreadyRegisteredError(Exception):
    """이미 가게가 등록된 판매자."""


class StorePaymentInfoAlreadyExistsError(Exception):
    """가게 결제 정보가 이미 등록되어 있음."""


class StorePaymentMissingError(Exception):
    """가게 마감 처리 시 포트원 secret_key 누락."""


class StoreImageDuplicateError(Exception):
    """초기 이미지 등록 시 이미 이미지가 있음."""


class StoreImageNotFoundError(Exception):
    """이미지 조회/삭제 시 대상 없음."""


class StoreImageMainDeleteError(Exception):
    """대표 이미지는 삭제할 수 없음."""


class StoreOperationReservationDuplicateError(Exception):
    """이미 예약이 존재함."""


class StoreOperationReservationNotFoundError(Exception):
    """변경 예약 없음."""


class StoreSNSNotFoundError(Exception):
    """등록된 SNS 정보 없음."""


class ProductNotFoundError(Exception):
    """상품 없음."""


class ProductAlreadyRegisteredError(Exception):
    """MVP 제한: 이미 상품 등록됨."""


class ProductStockReservationNotFoundError(Exception):
    """재고 예약 정보 없음."""


class ProductNutritionDuplicateError(Exception):
    """이미 등록된 영양 정보."""

    def __init__(self, duplicates: list):
        self.duplicates = duplicates
        super().__init__(f"중복: {duplicates}")


class ProductNutritionNotFoundError(Exception):
    """삭제 대상 영양 정보 없음."""

    def __init__(self, missing: list):
        self.missing = missing
        super().__init__(f"존재하지 않음: {missing}")


class ProductStockConflictError(Exception):
    """낙관적 락 충돌로 재고 변경 실패."""


class ProductStockInsufficientError(Exception):
    """재고 부족."""


class SellerNotFoundError(Exception):
    """판매자 없음."""


class SellerAlreadyWithdrawnError(Exception):
    """이미 탈퇴 처리됨."""


class SellerAlreadyActiveError(Exception):
    """이미 활성 상태 — 탈퇴 취소 불가."""


class SellerStoreOpenError(Exception):
    """가게 오픈 상태 → 탈퇴 불가."""


class SellerWithdrawalRecordNotFoundError(Exception):
    """탈퇴 기록 없음."""
