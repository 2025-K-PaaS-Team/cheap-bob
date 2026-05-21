"""PortOne 결제 게이트웨이 wrapper. stateless — 가게별 secret_key 를 인자로 받는다.

PortOne SDK 의 구체 예외 (`PortOnePaymentNotFoundError` / `PortOneTransientError`) 를
도메인 예외 (`PaymentVerificationError` / `PaymentRefundError`) 로 변환한다. infra 의 예외가
service/router 까지 leak 되지 않게 하는 경계 역할.

예외: `fetch_status` 는 sweeper 가 transient/permanent 를 구분해야 하므로 transient 만
``PortOneTransientError`` 그대로 leak — sweeper 가 catch 해 cart 를 다음 sweep 으로 미룬다.
"""
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
        """결제 검증 — PortOne 에 결제 진실 재조회 + amount tampering 검사.

        expected_amount: caller (cart_item.total_amount) 가 알고 있는 금액. PortOne 에 기록된
        실제 결제 amount 와 비교 — 불일치는 사용자가 PortOne 결제창에서 금액을 조작했음을 의미.

        Raises:
            PaymentVerificationError: 4xx / 5xx / 네트워크 / status != PAID / amount 불일치.
        """
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
            # PortOne 결제 amount 가 우리가 만든 cart 의 total_amount 와 다르다 = tampering.
            # 사용자가 결제창에서 금액을 임의 변경하거나 다른 결제를 끼워넣은 경우.
            raise PaymentVerificationError(
                f"결제 금액이 일치하지 않습니다 "
                f"(expected={expected_amount}, paid={payment.total_amount})",
            )
        return payment


    async def fetch_status(
        self, *, payment_id: str, secret_key: str,
    ) -> Optional[PortOnePayment]:
        """sweeper 가 만료 cart 의 진위를 확인할 때 사용.

        Returns:
            PortOnePayment — PortOne 측에 결제 기록이 있음 (status 는 caller 가 분기).
            None            — PortOne 측에 해당 결제 기록 없음 (사용자가 결제창 자체를 닫음).

        Raises:
            PortOneTransientError — 5xx / 네트워크. caller (sweeper) 가 cart 를 다음 sweep
                                     으로 미루도록 신호. ``verify`` 와 달리 wrap 하지 않는다.
        """
        try:
            return await self.portone_client.fetch_payment(
                payment_id, api_secret=secret_key,
            )
        except PortOnePaymentNotFoundError:
            return None


    async def refund(
        self, *, payment_id: str, secret_key: str, reason: str,
    ) -> Dict[str, Any]:
        """포트원 환불.

        Raises:
            PaymentRefundError: 4xx / 5xx / 네트워크 — caller 가 운영자 알람 결정.
        """
        try:
            return await self.portone_client.cancel_payment(
                payment_id, api_secret=secret_key, reason=reason,
            )
        except PortOnePaymentNotFoundError as e:
            raise PaymentRefundError(f"환불 처리 실패: {e}") from e
        except PortOneTransientError as e:
            raise PaymentRefundError(f"환불 게이트웨이 일시 장애: {e}") from e
