"""payment-svc 가 결제 확정 시 발송하는 예약 이메일.

backend 의 동명 모듈을 결제 알림 1종으로 trim. 다른 이벤트 (accept/cancel) 는
backend 가 자체 발송한다.
"""
from typing import Any, Dict
import pytz
from loguru import logger
from datetime import datetime

from app.core.email.template import reservation
from app.core.email.sender import email_sender


_KST = pytz.timezone("Asia/Seoul")


def _ts() -> str:
    return datetime.now(_KST).strftime("%Y년 %m월 %d일 %H:%M:%S")


async def _safe_send(*, recipient_email: str, subject: str, body: str, html_body: str) -> Dict[str, Any]:
    if not email_sender.is_configured():
        logger.warning("이메일 서비스가 설정되지 않음 - {}", recipient_email)
        return {"success": False, "message": "Email service not configured"}
    try:
        result = await email_sender.send(
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )
        if not result["success"]:
            logger.error(
                "[CRITICAL] 이메일 전송 실패 - 수신자={} 제목={} 사유={}",
                recipient_email, subject, result.get("message"),
            )
        return result
    except Exception:
        logger.exception(
            "[CRITICAL] 이메일 전송 중 예외 - 수신자={} 제목={}",
            recipient_email, subject,
        )
        return {"success": False, "message": "email send exception"}


async def send_reservation_email(customer_email: str) -> Dict[str, Any]:
    """payment confirm 직후 — 예약 등록 안내."""
    ts = _ts()
    return await _safe_send(
        recipient_email=customer_email,
        subject="[저렴한끼] 🎉 주문이 등록되었습니다!",
        body=reservation.get_reservation_text_template(ts, customer_email),
        html_body=reservation.get_reservation_html_template(ts, customer_email),
    )
