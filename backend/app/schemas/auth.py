from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserType(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: UserType


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True


class CustomerCreate(UserBase):
    pass


class SellerCreate(UserBase):
    pass


class CustomerInDB(UserBase):
    created_at: datetime
    
    class Config:
        from_attributes = True


class SellerInDB(UserBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

# Post 방식이었을 때, 필요했던
# class OAuthLoginRequest(BaseModel):
#     code: str
#     state: Optional[str] = None