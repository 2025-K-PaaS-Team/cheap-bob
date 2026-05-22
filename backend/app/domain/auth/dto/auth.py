from enum import Enum
from dataclasses import dataclass


class UserType(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"


@dataclass
class AuthResult:
    """OAuthService.authenticate 의 내부 결과.

    `conflict=True` 는 요청한 user_type 과 다른 종류로 이미 가입된 계정임을 뜻한다.
    이 경우 access_token 은 *실제로 가입된* 종류 기준으로 발급된다 (라우터가 이를 판별해 redirect 분기에 사용).
    """

    access_token: str
    user_type: UserType
    is_active: bool
    conflict: bool
    email: str
