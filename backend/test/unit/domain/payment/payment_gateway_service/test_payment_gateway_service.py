"""Tests for ``app.domain.payment.service.payment_gateway.PaymentGatewayService``.

PaymentGatewayService 는 PortOneClient 에 대한 얇은 wrapper 이므로, 검증 대상은:
  1) PortOneClient 가 호출되는 형태 (secret_key, payment_id, reason 가 전달되는지)
  2) PortOne 측 예외가 ``PaymentVerificationError`` / ``PaymentRefundError`` 로 변환되는지
"""
from unittest.mock import MagicMock, patch
import pytest

from app.domain.payment.service.exception import (
    PaymentRefundError,
    PaymentVerificationError,
)


# ────────────────────────────────────────────────────────────────────
# verify
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestVerify:

    async def test_returns_extracted_details_on_success(self, service):
        # PortOneClient 생성자 + get_payment + extract_payment_details 를 모두 mock.
        with patch(
            "app.domain.payment.service.payment_gateway.PortOneClient",
        ) as ClientCls:
            instance = MagicMock()
            instance.get_payment.return_value = {"raw": "payment-obj"}
            ClientCls.return_value = instance
            ClientCls.extract_payment_details = MagicMock(
                return_value={"amount": 10000, "payment_method": "CARD"},
            )

            result = await service.verify(payment_id="PAY_x", secret_key="sk_x")

            ClientCls.assert_called_once_with(secret_key="sk_x")
            instance.get_payment.assert_called_once_with("PAY_x")
            assert result == {"amount": 10000, "payment_method": "CARD"}


    async def test_wraps_portone_exception_to_verification_error(self, service):
        with patch(
            "app.domain.payment.service.payment_gateway.PortOneClient",
        ) as ClientCls:
            instance = MagicMock()
            instance.get_payment.side_effect = RuntimeError("PG down")
            ClientCls.return_value = instance

            with pytest.raises(PaymentVerificationError, match="결제 검증 실패"):
                await service.verify(payment_id="PAY_x", secret_key="sk_x")


# ────────────────────────────────────────────────────────────────────
# refund
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestRefund:

    async def test_returns_cancel_result_on_success(self, service):
        with patch(
            "app.domain.payment.service.payment_gateway.PortOneClient",
        ) as ClientCls:
            instance = MagicMock()
            instance.cancel_payment.return_value = {"refunded": True}
            ClientCls.return_value = instance

            result = await service.refund(
                payment_id="PAY_x", secret_key="sk_x", reason="단순 변심",
            )

            ClientCls.assert_called_once_with(secret_key="sk_x")
            instance.cancel_payment.assert_called_once_with(
                payment_id="PAY_x", reason="단순 변심",
            )
            assert result == {"refunded": True}


    async def test_wraps_portone_exception_to_refund_error(self, service):
        with patch(
            "app.domain.payment.service.payment_gateway.PortOneClient",
        ) as ClientCls:
            instance = MagicMock()
            instance.cancel_payment.side_effect = RuntimeError("PG down")
            ClientCls.return_value = instance

            with pytest.raises(PaymentRefundError, match="환불 처리 실패"):
                await service.refund(
                    payment_id="PAY_x", secret_key="sk_x", reason="단순 변심",
                )
