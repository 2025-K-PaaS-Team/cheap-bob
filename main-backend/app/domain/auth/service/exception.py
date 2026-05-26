class OAuthAuthenticationError(Exception):
    """OAuth provider 호출 또는 사용자 정보 파싱 단계에서 발생한 오류.

    `reason` 은 callback 라우터가 프론트 `/auth/error?reason=...` 로 그대로 전달한다.
    하위 클래스에서 override 하여 프론트 분기 코드를 세분화한다.
    """

    reason: str = "oauth_failed"


class OAuthEmailMissingError(OAuthAuthenticationError):
    """provider 가 email 을 제공하지 않은 경우."""

    reason: str = "email_missing"
