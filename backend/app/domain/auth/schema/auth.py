from pydantic import BaseModel

from app.domain.auth.dto.auth import UserType


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: UserType
