class OAuthAuthenticationError(Exception):
    """OAuth provider 호출 또는 사용자 정보 파싱 단계에서 발생한 오류."""


class OAuthEmailMissingError(OAuthAuthenticationError):
    """provider 가 email 을 제공하지 않은 경우."""


class CustomerNotFoundError(Exception):
    """customers 테이블에 매칭되는 row 없음."""


class SellerNotFoundError(Exception):
    """sellers 테이블에 매칭되는 row 없음."""
