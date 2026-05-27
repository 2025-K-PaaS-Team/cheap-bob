"""OrderRefundRequestedEventHandler 의 3개 분기 + dedupe 단위 테스트.

핵심 회귀 방지:
  - Happy path 에서 PaymentRefundCompletedPayload 가 schema 와 일치하는지 (v2 의 store_name /
    customer_id 누락 사고 방지).
  - failure 분기 (config_missing / portone_refused) 도 검증.
  - 중복 event_id 는 skip — try_mark 가 False 면 외부 호출 / outbox 발행 모두 없어야.
"""
from uuid import UUID
import pytest

from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
    PaymentRefundError,
    PaymentRefundTransientError,
)
from app.domain.payment.event.refund import (
    PaymentRefundCompletedPayload,
    PaymentRefundFailedPayload,
)


@pytest.mark.unit
class TestSuccessPath:
    """Happy path — schema v2 echo 누락 사고 회귀 방지 (가장 중요)."""

    async def test_emits_completed_with_all_v2_fields(
        self, handler, msg, v2_payload, payment_gateway_mock, enqueue_event_mock,
    ):
        await handler.handle(msg)

        # PortOne 호출 1회.
        payment_gateway_mock.refund.assert_awaited_once()

        # completed 이벤트 1회 발행.
        assert enqueue_event_mock.await_count == 1
        kwargs = enqueue_event_mock.await_args.kwargs
        assert kwargs["topic"] == "payment.refund.completed"
        assert kwargs["aggregate_id"] == "PAY_test"

        # ── 회귀 방지 핵심 ── completed payload 가 v2 schema 검증을 통과해야 한다.
        # PaymentRefundCompletedPayload 는 store_name / customer_id 가 required —
        # 이전 버그는 이 두 필드 누락으로 ValidationError 였다.
        validated = PaymentRefundCompletedPayload.model_validate(kwargs["payload"])
        assert validated.payment_id == v2_payload["payment_id"]
        assert validated.store_id == v2_payload["store_id"]
        assert validated.store_name == v2_payload["store_name"]
        assert validated.customer_id == v2_payload["customer_id"]
        assert validated.product_id == v2_payload["product_id"]
        assert validated.quantity == v2_payload["quantity"]
        assert validated.reason == v2_payload["reason"]


    async def test_marks_processed_event(
        self, handler, msg, processed_event_repo_mock, fixed_event_id,
    ):
        await handler.handle(msg)
        processed_event_repo_mock.try_mark.assert_awaited_once_with(
            event_id=UUID(fixed_event_id),
            topic="order.refund.requested",
        )


@pytest.mark.unit
class TestDedupe:
    """중복 메시지 처리 — try_mark False 면 외부 호출 / outbox 발행 모두 없어야."""

    async def test_skips_when_processed_event_already_recorded(
        self,
        handler, msg, processed_event_repo_mock,
        payment_gateway_mock, store_payment_info_mock, enqueue_event_mock,
    ):
        processed_event_repo_mock.try_mark.return_value = False

        await handler.handle(msg)

        # 핵심: PortOne 호출 / payment_info lookup / outbox 발행 모두 NOT 호출.
        payment_gateway_mock.refund.assert_not_awaited()
        store_payment_info_mock.get_complete_by_store.assert_not_awaited()
        enqueue_event_mock.assert_not_awaited()


@pytest.mark.unit
class TestConfigMissing:
    """가게 결제 설정 누락 → payment.refund.failed (kind=config_missing)."""

    async def test_emits_failed_event_when_payment_info_missing(
        self, handler, msg, store_payment_info_mock,
        payment_gateway_mock, enqueue_event_mock,
    ):
        store_payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoMissingError("결제 설정 없음")
        )

        await handler.handle(msg)

        # PortOne 호출 안 함 (lookup 단계에서 분기).
        payment_gateway_mock.refund.assert_not_awaited()

        # failed 이벤트 발행.
        assert enqueue_event_mock.await_count == 1
        kwargs = enqueue_event_mock.await_args.kwargs
        assert kwargs["topic"] == "payment.refund.failed"
        failed = PaymentRefundFailedPayload.model_validate(kwargs["payload"])
        assert failed.error_kind == "config_missing"
        assert "결제 설정 없음" in (failed.error_detail or "")


    async def test_emits_failed_event_when_payment_info_incomplete(
        self, handler, msg, store_payment_info_mock, enqueue_event_mock,
    ):
        store_payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoIncompleteError("일부 필드 누락")
        )

        await handler.handle(msg)

        kwargs = enqueue_event_mock.await_args.kwargs
        assert kwargs["topic"] == "payment.refund.failed"
        failed = PaymentRefundFailedPayload.model_validate(kwargs["payload"])
        assert failed.error_kind == "config_missing"


@pytest.mark.unit
class TestPortOneRefused:
    """PortOne 4xx terminal → payment.refund.failed (kind=portone_refused)."""

    async def test_emits_failed_event_on_terminal_portone_error(
        self, handler, msg, payment_gateway_mock, enqueue_event_mock,
    ):
        payment_gateway_mock.refund.side_effect = PaymentRefundError(
            "PortOne cancel 401",
        )

        await handler.handle(msg)

        # PortOne 호출 발생.
        payment_gateway_mock.refund.assert_awaited_once()

        # failed 이벤트 발행.
        kwargs = enqueue_event_mock.await_args.kwargs
        assert kwargs["topic"] == "payment.refund.failed"
        failed = PaymentRefundFailedPayload.model_validate(kwargs["payload"])
        assert failed.error_kind == "portone_refused"
        assert "PortOne cancel 401" in (failed.error_detail or "")


@pytest.mark.unit
class TestTransient:
    """PortOne 5xx/네트워크 → raise — consumer offset 미커밋 → 재배달."""

    async def test_raises_transient_so_message_retries(
        self, handler, msg, payment_gateway_mock, enqueue_event_mock,
    ):
        payment_gateway_mock.refund.side_effect = PaymentRefundTransientError(
            "PortOne 5xx",
        )

        with pytest.raises(PaymentRefundTransientError):
            await handler.handle(msg)

        # transient 면 outbox 발행 안 함 (rollback 으로 사라짐).
        enqueue_event_mock.assert_not_awaited()


@pytest.mark.unit
class TestPayloadValidation:
    """malformed payload — handler 가 skip (raise 하지 않음, 무한 재배달 방지)."""

    async def test_skips_on_payload_validation_error(
        self, handler, make_msg, fixed_event_id,
        payment_gateway_mock, enqueue_event_mock,
    ):
        # v2 필수 필드 누락 payload.
        bad_msg = make_msg(
            event_id=fixed_event_id,
            payload={"payment_id": "PAY_bad"},  # 나머지 필드 누락.
        )

        # raise 안 하고 skip — 무한 재배달 방지.
        await handler.handle(bad_msg)

        payment_gateway_mock.refund.assert_not_awaited()
        enqueue_event_mock.assert_not_awaited()
