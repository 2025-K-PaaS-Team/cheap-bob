"""PortOne 결제 게이트웨이 wrapper. stateless — 가게별 secret_key 를 인자로 받는다."""
from typing import Dict

from app.domain.payment.service.exception import (
    PaymentRefundError,
    PaymentVerificationError,
)
from app.core.portone import PortOneClient


class PaymentGatewayService:
    """PortOne API 호출 — 검증 / 환불. stateless 라 Singleton OK."""

    async def verify(self, *, payment_id: str, secret_key: str) -> Dict:
        """결제 검증. 실패 시 `PaymentVerificationError`."""
        try:
            client = PortOneClient(secret_key=secret_key)
            payment = client.get_payment(payment_id)
            return PortOneClient.extract_payment_details(payment)
        except Exception as e:
            raise PaymentVerificationError(f"결제 검증 실패: {e}")


    async def refund(self, *, payment_id: str, secret_key: str, reason: str) -> Dict:
        """포트원 환불. 실패 시 `PaymentRefundError`."""
        try:
            client = PortOneClient(secret_key=secret_key)
            return client.cancel_payment(payment_id=payment_id, reason=reason)
        except Exception as e:
            raise PaymentRefundError(f"환불 처리 실패: {e}")
