class CustomerNotFoundError(Exception):
    """소비자 계정을 찾을 수 없음."""


class CustomerAlreadyRegisteredError(Exception):
    """이미 프로필이 등록된 소비자."""


class CustomerAlreadyWithdrawnError(Exception):
    """이미 탈퇴 처리된 소비자."""


class CustomerActiveOrdersExistError(Exception):
    """진행 중인 주문이 있어 탈퇴할 수 없음."""


class WithdrawalRecordNotFoundError(Exception):
    """탈퇴 기록이 없어 취소할 수 없음."""


class CustomerAlreadyActiveError(Exception):
    """탈퇴 취소를 시도하지만 이미 활성 상태."""


class CustomerDetailNotFoundError(Exception):
    """소비자 상세 정보가 없음."""


class PreferenceDuplicateError(Exception):
    """선호도 추가 시 이미 등록된 항목 존재."""

    def __init__(self, duplicates: list[str]):
        self.duplicates = duplicates
        super().__init__(f"이미 등록됨: {', '.join(duplicates)}")


class PreferenceNotFoundError(Exception):
    """삭제 대상 선호도가 존재하지 않음."""


class StoreNotFoundError(Exception):
    """[TRANSITIONAL] 검색/즐겨찾기 대상 가게가 없음. seller 도메인 분리 시 이관."""


class FavoriteAlreadyExistsError(Exception):
    """이미 즐겨찾기에 등록된 가게."""


class FavoriteNotFoundError(Exception):
    """즐겨찾기에서 찾을 수 없는 가게."""
