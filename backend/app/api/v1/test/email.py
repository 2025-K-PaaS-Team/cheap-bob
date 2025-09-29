from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from loguru import logger
from datetime import datetime
from typing import Optional, Literal

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentCustomerDep
from services.email import email_service

router = APIRouter(prefix="/email")


class EmailRequest(BaseModel):
    subject: str = "테스트 이메일"
    body: str = "안녕하세요 칩밥입니다."
    html_body: Optional[str] = None


class EmailResponse(BaseModel):
    success: bool
    message: str
    sent_at: datetime


class TemplateEmailRequest(BaseModel):
    template_type: Literal["default", "welcome", "order"] = "default"


@router.post("/send", response_model=EmailResponse,
    responses=create_error_responses({
        400: "이메일 전송 실패",
        401: ["인증 정보가 없음", "토큰 만료"],
        500: "서버 에러"
    })
)
async def send_test_email(
    request: EmailRequest,
    current_user: CurrentCustomerDep
):
    """
    테스트용 이메일 전송 API
    """
    
    if not email_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP 설정이 구성되지 않았습니다. 환경 변수를 확인하세요."
        )
    
    recipient_email = current_user["sub"]
    
    logger.info(f"이메일 전송 시도 - 수신자: {recipient_email}")
    
    # 이메일 전송
    result = email_service.send(
        recipient_email=recipient_email,
        subject=request.subject,
        body=request.body,
        html_body=request.html_body
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return EmailResponse(**result)


@router.post("/send-template", response_model=EmailResponse,
    responses=create_error_responses({
        400: "이메일 전송 실패",
        401: ["인증 정보가 없음", "토큰 만료"],
        500: "서버 에러"
    })
)
async def send_template_email(
    request: TemplateEmailRequest,
    current_user: CurrentCustomerDep
):
    """
    템플릿 이메일 전송 API - 미리 정의된 템플릿으로 이메일 전송
    
    템플릿 타입:
    - default: 기본 테스트 이메일
    - welcome: 회원가입 환영 이메일
    - order: 주문 확인 이메일
    """
    
    if not email_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP 설정이 구성되지 않았습니다. 환경 변수를 확인하세요."
        )
    
    recipient_email = current_user["sub"]
    
    logger.info(f"템플릿 이메일 전송 시도 - 수신자: {recipient_email}, 템플릿: {request.template_type}")
    
    result = email_service.send_template(
        recipient_email=recipient_email,
        template_type=request.template_type
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return EmailResponse(**result)