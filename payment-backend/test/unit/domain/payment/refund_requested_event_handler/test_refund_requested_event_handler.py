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
from app.core.kafka.consumer import TerminalEventError


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
    """PortOne 4xx terminal → payment.refund.failed (kind=portone_refused).

    Race fix 후: PaymentRefundError 받으면 fetch_status 로 진위 확인 분기.
      - status=CANCELLED → completed 흡수 (race)
      - 그 외 (None / PAID / FAILED 등) → failed 발행
    """

    async def test_emits_failed_event_when_not_cancelled(
        self, handler, msg, payment_gateway_mock, enqueue_event_mock,
    ):
        # refund 4xx + fetch_status=None (default) → 진짜 거부 → failed.
        payment_gateway_mock.refund.side_effect = PaymentRefundError(
            "PortOne cancel 401",
        )

        await handler.handle(msg)

        # PortOne refund + fetch_status 모두 호출됨.
        payment_gateway_mock.refund.assert_awaited_once()
        payment_gateway_mock.fetch_status.assert_awaited_once()

        # failed 이벤트 발행.
        kwargs = enqueue_event_mock.await_args.kwargs
        assert kwargs["topic"] == "payment.refund.failed"
        failed = PaymentRefundFailedPayload.model_validate(kwargs["payload"])
        assert failed.error_kind == "portone_refused"
        assert "PortOne cancel 401" in (failed.error_detail or "")


@pytest.mark.unit
class TestRaceAbsorption:
    """수동 cancel 흐름이 먼저 PortOne 취소 완료 → 워커 이벤트가 뒤늦게 도달 → 흡수.

    payment-backend refund 호출이 4xx 받지만 fetch_status 가 CANCELLED 확인 →
    completed 발행 (failed 아님). main-backend completed 핸들러는 quantity=0 으로
    이메일/restore skip 처리 — 중복 방지.
    """

    async def test_absorbs_to_completed_when_portone_already_cancelled(
        self, handler, msg, v2_payload,
        payment_gateway_mock, enqueue_event_mock,
    ):
        from types import SimpleNamespace
        from app.core.portone import PortOnePaymentStatus

        # race: refund 시도 시 PortOne 이 이미 cancelled 상태라 4xx 반환.
        payment_gateway_mock.refund.side_effect = PaymentRefundError(
            "PortOne cancel 400: already cancelled",
        )
        # fetch_status 가 CANCELLED 확인 — race 신호.
        payment_gateway_mock.fetch_status.return_value = SimpleNamespace(
            status=PortOnePaymentStatus.CANCELLED,
        )

        await handler.handle(msg)

        # 진위 확인 1회.
        payment_gateway_mock.fetch_status.assert_awaited_once()

        # completed 이벤트 발행 (failed 아님).
        assert enqueue_event_mock.await_count == 1
        kwargs = enqueue_event_mock.await_args.kwargs
        assert kwargs["topic"] == "payment.refund.completed"
        completed = PaymentRefundCompletedPayload.model_validate(kwargs["payload"])
        # echo 검증 — race 흡수 경로도 v2 필드 모두 보존.
        assert completed.payment_id == v2_payload["payment_id"]
        assert completed.store_name == v2_payload["store_name"]
        assert completed.customer_id == v2_payload["customer_id"]


    async def test_raises_transient_when_fetch_status_fails(
        self, handler, msg, payment_gateway_mock, enqueue_event_mock,
    ):
        """진위 확인 자체가 transient 실패면 결정 보류 → retry."""
        from app.core.portone import PortOneTransientError

        payment_gateway_mock.refund.side_effect = PaymentRefundError("PortOne 4xx")
        payment_gateway_mock.fetch_status.side_effect = PortOneTransientError(
            "PortOne 5xx",
        )

        with pytest.raises(PaymentRefundTransientError):
            await handler.handle(msg)

        # 결정 못함 — outbox 발행 없음 (rollback).
        enqueue_event_mock.assert_not_awaited()


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
    """malformed payload → TerminalEventError → Runner 가 DLQ 격리."""

    async def test_raises_terminal_on_payload_validation_error(
        self, handler, make_msg, fixed_event_id,
        payment_gateway_mock, enqueue_event_mock,
    ):
        # v2 필수 필드 누락 payload.
        bad_msg = make_msg(
            event_id=fixed_event_id,
            payload={"payment_id": "PAY_bad"},  # 나머지 필드 누락.
        )

        # TerminalEventError raise — Runner 가 catch 해서 즉시 DLQ 로 격리.
        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)

        payment_gateway_mock.refund.assert_not_awaited()
        enqueue_event_mock.assert_not_awaited()


    async def test_raises_terminal_on_missing_event_id_header(
        self, handler, v2_payload,
        payment_gateway_mock, enqueue_event_mock,
    ):
        from types import SimpleNamespace
        msg = SimpleNamespace(
            headers=[],  # event_id 헤더 없음.
            value=v2_payload,
            offset=99,
        )

        with pytest.raises(TerminalEventError):
            await handler.handle(msg)

        payment_gateway_mock.refund.assert_not_awaited()
        enqueue_event_mock.assert_not_awaited()
