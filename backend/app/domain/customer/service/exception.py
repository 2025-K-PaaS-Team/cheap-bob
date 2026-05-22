from app.core.exceptions import DomainError


class CustomerNotFoundError(DomainError):
    """소비자 계정을 찾을 수 없음."""
    status_code = 404


class CustomerAlreadyRegisteredError(DomainError):
    """이미 프로필이 등록된 소비자."""
    status_code = 400


class CustomerAlreadyWithdrawnError(DomainError):
    """이미 탈퇴 처리된 소비자."""
    status_code = 409


class CustomerActiveOrdersExistError(DomainError):
    """진행 중인 주문이 있어 탈퇴할 수 없음."""
    status_code = 403


class WithdrawalRecordNotFoundError(DomainError):
    """탈퇴 기록이 없어 취소할 수 없음."""
    status_code = 404


class CustomerAlreadyActiveError(DomainError):
    """탈퇴 취소를 시도하지만 이미 활성 상태."""
    status_code = 409


class CustomerDetailNotFoundError(DomainError):
    """소비자 상세 정보가 없음."""
    status_code = 404


class PreferenceDuplicateError(DomainError):
    """선호도 추가 시 이미 등록된 항목 존재."""
    status_code = 400

    def __init__(self, duplicates: list[str]):
        self.duplicates = duplicates
        super().__init__(f"이미 등록됨: {', '.join(duplicates)}")


class PreferenceNotFoundError(DomainError):
    """삭제 대상 선호도가 존재하지 않음."""
    status_code = 404


class FavoriteAlreadyExistsError(DomainError):
    """이미 즐겨찾기에 등록된 가게."""
    status_code = 409


class FavoriteNotFoundError(DomainError):
    """즐겨찾기에서 찾을 수 없는 가게."""
    status_code = 404
