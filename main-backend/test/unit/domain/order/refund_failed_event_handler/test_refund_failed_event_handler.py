"""PaymentRefundFailedEventHandler 전 분기 단위 테스트.

핵심 검증:
  - 모든 error_kind (config_missing, portone_refused) 에서 CRITICAL 알람.
  - error_detail=None Optional 처리.
  - dedupe — 중복 이벤트는 CRITICAL 안 울림 (info 만).
  - validation 실패 → TerminalEventError (DLQ).
  - 본 핸들러는 DB 상태/재고/이메일 등 부수효과 없음 (failed 는 운영자 보정 시그널만).
  - try_mark 호출 args (event_id + topic) 정확성.
"""
from uuid import UUID
import pytest

from app.core.kafka.consumer import TerminalEventError


TOPIC = "payment.refund.failed"


@pytest.mark.unit
class TestCriticalAlarmEmission:
    """신규 failure 이벤트 → CRITICAL 로그 (kind/detail 모두 포함)."""

    async def test_emits_critical_for_config_missing(
        self, handler, msg, config_missing_payload, mock_logger,
    ):
        await handler.handle(msg)

        mock_logger.error.assert_called_once()
        args = mock_logger.error.call_args.args
        # format string + positional args 안에 핵심 식별자 모두 포함.
        combined = " ".join(str(a) for a in args)
        assert "[CRITICAL]" in combined
        assert config_missing_payload["payment_id"] in combined
        assert config_missing_payload["store_id"] in combined
        assert "config_missing" in combined
        assert config_missing_payload["error_detail"] in combined


    async def test_emits_critical_for_portone_refused(
        self, handler, make_msg, fixed_event_id, portone_refused_payload, mock_logger,
    ):
        msg = make_msg(event_id=fixed_event_id, payload=portone_refused_payload)

        await handler.handle(msg)

        mock_logger.error.assert_called_once()
        combined = " ".join(str(a) for a in mock_logger.error.call_args.args)
        assert "portone_refused" in combined
        assert portone_refused_payload["payment_id"] in combined


    async def test_handles_optional_error_detail_none(
        self, handler, make_msg, fixed_event_id, mock_logger,
    ):
        """error_detail 은 Optional — None 이어도 안전하게 로그."""
        msg = make_msg(
            event_id=fixed_event_id,
            payload={
                "payment_id": "PAY_no_detail",
                "store_id": "STR_x",
                "error_kind": "portone_refused",
                # error_detail 생략 — pydantic default=None
            },
        )

        # raise 안 함.
        await handler.handle(msg)

        mock_logger.error.assert_called_once()
        # detail 자리에 None 이 포함됨 — format string 이 깨지지 않는지 확인.
        combined = " ".join(str(a) for a in mock_logger.error.call_args.args)
        assert "None" in combined


@pytest.mark.unit
class TestDedupe:
    """중복 이벤트 → try_mark False → CRITICAL 안 울림 (info skip 로그만)."""

    async def test_skips_critical_alarm_when_try_mark_false(
        self, handler, msg, processed_event_repo_mock, mock_logger,
    ):
        processed_event_repo_mock.try_mark.return_value = False

        await handler.handle(msg)

        # 핵심: 중복 알람 spam 방지 — error 호출 X.
        mock_logger.error.assert_not_called()
        # info 로그는 (중복 skip 알림용) 호출됨.
        assert mock_logger.info.call_count >= 1
        info_combined = " ".join(
            str(a) for c in mock_logger.info.call_args_list for a in c.args
        )
        assert "중복" in info_combined or "skip" in info_combined.lower()


@pytest.mark.unit
class TestProcessedEventLedger:
    """try_mark 호출 인자 정확성."""

    async def test_try_mark_called_with_topic_and_uuid_event_id(
        self, handler, msg, processed_event_repo_mock, fixed_event_id,
    ):
        await handler.handle(msg)

        processed_event_repo_mock.try_mark.assert_awaited_once()
        kw = processed_event_repo_mock.try_mark.await_args.kwargs
        assert kw["topic"] == TOPIC
        assert kw["event_id"] == UUID(fixed_event_id)


@pytest.mark.unit
class TestValidation:
    """파싱/검증 실패 → TerminalEventError → DLQ 격리."""

    async def test_raises_terminal_on_payload_field_missing(
        self, handler, make_msg, fixed_event_id, mock_logger,
    ):
        """error_kind 누락 (required) → 검증 실패."""
        bad_msg = make_msg(
            event_id=fixed_event_id,
            payload={"payment_id": "PAY_bad", "store_id": "STR_x"},
        )

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)

        # CRITICAL alarm 안 울림 — DLQ 로 처리됨.
        mock_logger.error.assert_not_called()


    async def test_raises_terminal_on_payload_none(
        self, handler, make_msg, fixed_event_id,
    ):
        bad_msg = make_msg(event_id=fixed_event_id, payload=None)

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)


    async def test_raises_terminal_when_event_id_header_missing(
        self, handler, make_msg, config_missing_payload, mock_logger,
    ):
        bad_msg = make_msg(event_id=None, payload=config_missing_payload)

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)

        mock_logger.error.assert_not_called()


    async def test_raises_terminal_when_event_id_not_uuid(
        self, handler, make_msg, config_missing_payload,
    ):
        bad_msg = make_msg(event_id="not-a-uuid", payload=config_missing_payload)

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)


@pytest.mark.unit
class TestNoSideEffects:
    """failed 핸들러는 DB 상태/재고/이메일 등 부수효과 0 — 운영자 보정 시그널만."""

    async def test_handler_has_no_repository_or_service_dependencies(
        self, handler,
    ):
        """생성자가 uow 만 의존 — 다른 도메인 서비스 의존성 0 (의도된 제약)."""
        # __init__ 이 uow 외 다른 dep 받지 않는다 — 부수효과 없음의 구조적 보장.
        assert hasattr(handler, "uow")
        # 다른 비즈니스 객체 없음 — 그래서 잘못 호출할 수 있는 경로 자체가 없음.
        attrs = [a for a in vars(handler) if not a.startswith("_")]
        assert attrs == ["uow"], (
            f"failed 핸들러는 uow 외 의존성 없어야 함 (부수효과 0 보장): {attrs}"
        )


    async def test_service_propagation_try_mark_exception(
        self, handler, msg, processed_event_repo_mock, mock_logger,
    ):
        """try_mark DB 오류는 그대로 raise — Runner 가 retry/DLQ 결정."""
        processed_event_repo_mock.try_mark.side_effect = RuntimeError("DB down")

        with pytest.raises(RuntimeError, match="DB down"):
            await handler.handle(msg)

        # try_mark 가 실패하면 CRITICAL 알람도 출력 안 됨.
        mock_logger.error.assert_not_called()
