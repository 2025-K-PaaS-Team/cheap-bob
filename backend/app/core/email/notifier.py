"""도메인 이벤트별 이메일 dispatch 헬퍼.

함수명은 도메인 이벤트 (reservation/accept/customer_cancel/seller_cancel) 를 가리키지만
**import graph 상 도메인 자산을 의존하지 않는다** — core/email/sender 와 template 만 사용.

각 함수는 fire-and-forget 패턴 (background_tasks.add_task 로 호출). 
실패해도 예외를 던지지 않고 result dict 로 표시.
"""
from typing import Any, Dict
import pytz
from loguru import logger
from datetime import datetime

from app.core.email.template import (
    accept,
    customer_cancel,
    reservation,
    seller_cancel,
)
from app.core.email.sender import email_sender


_KST = pytz.timezone("Asia/Seoul")


def _ts() -> str:
    return datetime.now(_KST).strftime("%Y년 %m월 %d일 %H:%M:%S")


async def _safe_send(*, recipient_email: str, subject: str, body: str, html_body: str) -> Dict[str, Any]:
    if not email_sender.is_configured():
        logger.warning("이메일 서비스가 설정되지 않음")
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
                f"이메일 전송 실패: {recipient_email} - {result.get('message')}",
            )
        return result
    except Exception as e:
        logger.error(f"이메일 전송 중 예외: {e}")
        return {"success": False, "message": str(e)}


async def send_reservation_email(customer_email: str) -> Dict[str, Any]:
    """payment confirm 직후 — 예약 등록 안내."""
    ts = _ts()
    return await _safe_send(
        recipient_email=customer_email,
        subject="[저렴한끼] 🎉 주문이 등록되었습니다!",
        body=reservation.get_reservation_text_template(ts, customer_email),
        html_body=reservation.get_reservation_html_template(ts, customer_email),
    )


async def send_order_accepted_email(
    customer_email: str, store_name: str,
) -> Dict[str, Any]:
    """seller accept 직후 — 픽업 확정 안내."""
    ts = _ts()
    return await _safe_send(
        recipient_email=customer_email,
        subject="[저렴한끼] 🎉 픽업이 확정되었습니다!",
        body=accept.get_accept_text_template(ts, customer_email, store_name),
        html_body=accept.get_accept_html_template(ts, customer_email, store_name),
    )


async def send_customer_cancel_email(
    customer_email: str, store_name: str,
) -> Dict[str, Any]:
    """customer 가 직접 주문 취소 — 취소 안내."""
    ts = _ts()
    return await _safe_send(
        recipient_email=customer_email,
        subject="[저렴한끼] 주문이 취소되었습니다.",
        body=customer_cancel.get_customer_cancel_text_template(
            ts, customer_email, store_name,
        ),
        html_body=customer_cancel.get_cusotmer_cancel_html_template(
            ts, customer_email, store_name,
        ),
    )


async def send_seller_cancel_email(
    customer_email: str, store_name: str,
) -> Dict[str, Any]:
    """seller 가 주문 취소 — 가게 취소 안내."""
    ts = _ts()
    return await _safe_send(
        recipient_email=customer_email,
        subject="[저렴한끼] 가게가 주문을 취소하였습니다.",
        body=seller_cancel.get_seller_cancel_text_template(
            ts, customer_email, store_name,
        ),
        html_body=seller_cancel.get_seller_cancel_html_template(
            ts, customer_email, store_name,
        ),
    )
