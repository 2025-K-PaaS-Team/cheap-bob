from enum import Enum

from pydantic import BaseModel


class UserType(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: UserType