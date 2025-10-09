from pydantic import BaseModel

class WithdrawResponse(BaseModel):
    """회원 탈퇴 관련 응답 모델"""
    message: str
    access_token: str