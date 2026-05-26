"""가게 결제 정보 register / check 의 외부 (frontend) request/response 모델.

payment 도메인은 payment-backend 로 MSA 분리됐지만, 1차 가입 흐름의 결제 정보 등록은
seller 도메인의 register 라우터가 owner — 따라서 schema 도 seller 측에 둔다. main-backend 가
받은 입력을 InternalPaymentClient 로 위임하면 client 내부 DTO 로 매핑된다.

내부 service-to-service DTO 는 ``app.core.internal_client.payment`` 에 별도 정의 (shared
패턴 미적용 정책).
"""
from pydantic import BaseModel, Field


class StorePaymentInfoCreateRequest(BaseModel):
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
    portone_secret_key: str = Field(..., min_length=1, description="포트원 시크릿 키")


class StorePaymentInfoCheckResponse(BaseModel):
    is_exist: bool = Field(..., description="결제 정보 등록 여부")
