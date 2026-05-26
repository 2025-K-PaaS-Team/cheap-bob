"""Tests for ``app.domain.payment.service.payment_gateway.PaymentGatewayService``.

PaymentGatewayService 는 PortOnePaymentClient 에 대한 얇은 wrapper. 검증 대상:
  1) PortOne client 가 호출되는 형태 (payment_id, api_secret, reason 가 전달되는지)
  2) PortOne 측 예외 (NotFound/Transient) 가 도메인 예외로 변환되는지
  3) status != PAID 면 verify 가 PaymentVerificationError 를 던지는지
"""
import pytest

from app.domain.payment.service.exception import (
    PaymentRefundError,
    PaymentVerificationError,
)
from app.core.portone import (
    PortOnePayment,
    PortOnePaymentNotFoundError,
    PortOnePaymentStatus,
    PortOneTransientError,
)


def _paid(payment_id: str = "PAY_x", amount: int = 10000) -> PortOnePayment:
    return PortOnePayment(
        payment_id=payment_id,
        status=PortOnePaymentStatus.PAID,
        total_amount=amount,
        currency="KRW",
        order_name="치킨 1개",
        payment_method="CARD",
        store_id=None,
    )


# ────────────────────────────────────────────────────────────────────
# verify
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestVerify:

    async def test_returns_payment_on_paid_with_matching_amount(
        self, service, portone_client_mock,
    ):
        portone_client_mock.fetch_payment.return_value = _paid()

        result = await service.verify(
            payment_id="PAY_x", secret_key="sk_x", expected_amount=10000,
        )

        portone_client_mock.fetch_payment.assert_awaited_once_with(
            "PAY_x", api_secret="sk_x",
        )
        assert result.status == PortOnePaymentStatus.PAID
        assert result.total_amount == 10000


    async def test_raises_when_amount_tampered(self, service, portone_client_mock):
        # PortOne 응답 amount 가 cart.total_amount 와 다른 케이스 — tampering 차단.
        portone_client_mock.fetch_payment.return_value = _paid(amount=1000)

        with pytest.raises(PaymentVerificationError, match="금액이 일치하지 않습니다"):
            await service.verify(
                payment_id="PAY_x", secret_key="sk_x", expected_amount=10000,
            )


    async def test_raises_when_not_paid(self, service, portone_client_mock):
        not_paid = PortOnePayment(
            payment_id="PAY_x",
            status=PortOnePaymentStatus.FAILED,
            total_amount=0,
            currency="KRW",
            order_name=None,
            payment_method=None,
            store_id=None,
        )
        portone_client_mock.fetch_payment.return_value = not_paid

        with pytest.raises(PaymentVerificationError, match="완료 상태가 아닙니다"):
            await service.verify(
                payment_id="PAY_x", secret_key="sk_x", expected_amount=10000,
            )


    async def test_wraps_not_found_to_verification_error(self, service, portone_client_mock):
        portone_client_mock.fetch_payment.side_effect = PortOnePaymentNotFoundError("404")

        with pytest.raises(PaymentVerificationError, match="결제 검증 실패"):
            await service.verify(
                payment_id="PAY_x", secret_key="sk_x", expected_amount=10000,
            )


    async def test_wraps_transient_to_verification_error(self, service, portone_client_mock):
        portone_client_mock.fetch_payment.side_effect = PortOneTransientError("5xx")

        with pytest.raises(PaymentVerificationError, match="일시 장애"):
            await service.verify(
                payment_id="PAY_x", secret_key="sk_x", expected_amount=10000,
            )


# ────────────────────────────────────────────────────────────────────
# fetch_status (sweeper 전용 — verify 와 달리 transient 를 wrap 하지 않음)
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestFetchStatus:

    async def test_returns_payment_when_present(self, service, portone_client_mock):
        portone_client_mock.fetch_payment.return_value = _paid()
        result = await service.fetch_status(
            payment_id="PAY_x", secret_key="sk_x",
        )
        portone_client_mock.fetch_payment.assert_awaited_once_with(
            "PAY_x", api_secret="sk_x",
        )
        assert result is not None
        assert result.status == PortOnePaymentStatus.PAID


    async def test_returns_none_when_portone_has_no_record(
        self, service, portone_client_mock,
    ):
        """사용자가 결제창만 열고 닫음 — PortOne 측 4xx → None 반환 (= 결제 미수행)."""
        portone_client_mock.fetch_payment.side_effect = PortOnePaymentNotFoundError("404")
        result = await service.fetch_status(
            payment_id="PAY_x", secret_key="sk_x",
        )
        assert result is None


    async def test_propagates_transient_for_sweeper_retry(
        self, service, portone_client_mock,
    ):
        """5xx/timeout 은 verify 처럼 wrap 하지 않음 — sweeper 가 catch 해 다음 sweep 으로 미룬다."""
        portone_client_mock.fetch_payment.side_effect = PortOneTransientError("5xx")
        with pytest.raises(PortOneTransientError):
            await service.fetch_status(payment_id="PAY_x", secret_key="sk_x")


    async def test_returns_non_paid_status_as_is(self, service, portone_client_mock):
        """status 분기는 caller 책임 — fetch_status 는 status 와 관계없이 객체 그대로 반환."""
        failed = PortOnePayment(
            payment_id="PAY_x",
            status=PortOnePaymentStatus.FAILED,
            total_amount=0,
            currency="KRW",
            order_name=None,
            payment_method=None,
            store_id=None,
        )
        portone_client_mock.fetch_payment.return_value = failed
        result = await service.fetch_status(
            payment_id="PAY_x", secret_key="sk_x",
        )
        assert result is failed
        assert result.status == PortOnePaymentStatus.FAILED


# ────────────────────────────────────────────────────────────────────
# refund
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestRefund:

    async def test_returns_cancel_result_on_success(self, service, portone_client_mock):
        portone_client_mock.cancel_payment.return_value = {"refunded": True}

        result = await service.refund(
            payment_id="PAY_x", secret_key="sk_x", reason="단순 변심",
        )

        portone_client_mock.cancel_payment.assert_awaited_once_with(
            "PAY_x", api_secret="sk_x", reason="단순 변심",
        )
        assert result == {"refunded": True}


    async def test_wraps_not_found_to_refund_error(self, service, portone_client_mock):
        portone_client_mock.cancel_payment.side_effect = PortOnePaymentNotFoundError("404")

        with pytest.raises(PaymentRefundError, match="환불 처리 실패"):
            await service.refund(
                payment_id="PAY_x", secret_key="sk_x", reason="단순 변심",
            )


    async def test_wraps_transient_to_refund_error(self, service, portone_client_mock):
        portone_client_mock.cancel_payment.side_effect = PortOneTransientError("network")

        with pytest.raises(PaymentRefundError, match="일시 장애"):
            await service.refund(
                payment_id="PAY_x", secret_key="sk_x", reason="단순 변심",
            )
