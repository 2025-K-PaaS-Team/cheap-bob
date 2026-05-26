"""PortOne 결제 게이트웨이 wrapper. stateless — 가게별 secret_key 를 인자로 받는다."""
from typing import Any, Dict, Optional

from app.domain.payment.service.exception import (
    PaymentRefundError,
    PaymentVerificationError,
)
from app.core.portone import (
    PortOnePayment,
    PortOnePaymentClient,
    PortOnePaymentNotFoundError,
    PortOnePaymentStatus,
    PortOneTransientError,
)


class PaymentGatewayService:
    """PortOne API 호출 — 검증 / 환불. stateless 라 Singleton OK."""

    def __init__(self, portone_client: PortOnePaymentClient):
        self.portone_client = portone_client


    async def verify(
        self, *, payment_id: str, secret_key: str, expected_amount: int,
    ) -> PortOnePayment:
        """결제 검증 — PortOne 에 결제 진실 재조회 + amount tampering 검사."""
        try:
            payment = await self.portone_client.fetch_payment(
                payment_id, api_secret=secret_key,
            )
        except PortOnePaymentNotFoundError as e:
            raise PaymentVerificationError(f"결제 검증 실패: {e}") from e
        except PortOneTransientError as e:
            raise PaymentVerificationError(f"결제 게이트웨이 일시 장애: {e}") from e

        if payment.status != PortOnePaymentStatus.PAID:
            raise PaymentVerificationError(
                f"결제가 완료 상태가 아닙니다 (status={payment.status.value})",
            )
        if payment.total_amount != expected_amount:
            raise PaymentVerificationError(
                f"결제 금액이 일치하지 않습니다 "
                f"(expected={expected_amount}, paid={payment.total_amount})",
            )
        return payment


    async def fetch_status(
        self, *, payment_id: str, secret_key: str,
    ) -> Optional[PortOnePayment]:
        """sweeper 가 만료 cart 의 진위를 확인할 때 사용."""
        try:
            return await self.portone_client.fetch_payment(
                payment_id, api_secret=secret_key,
            )
        except PortOnePaymentNotFoundError:
            return None


    async def refund(
        self, *, payment_id: str, secret_key: str, reason: str,
    ) -> Dict[str, Any]:
        """포트원 환불."""
        try:
            return await self.portone_client.cancel_payment(
                payment_id, api_secret=secret_key, reason=reason,
            )
        except PortOnePaymentNotFoundError as e:
            raise PaymentRefundError(f"환불 처리 실패: {e}") from e
        except PortOneTransientError as e:
            raise PaymentRefundError(f"환불 게이트웨이 일시 장애: {e}") from e
