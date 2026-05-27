"""SellerStoreWithdrawnEventHandler 전 분기 단위 테스트.

핵심 검증:
  - happy path (row 존재/부재 — 멱등성)
  - dedupe (중복 event_id)
  - 모든 validation 경로 → TerminalEventError (DLQ 격리)
  - 서비스 예외 → handler raise (Runner retry)
  - try_mark args 정확성 (event_id + topic)
  - 로그 인자에 deleted 값 정확히 들어가는지
"""
from uuid import UUID
import pytest

from app.core.kafka.consumer import TerminalEventError


TOPIC = "seller.store.withdrawn"


@pytest.mark.unit
class TestSuccessPath:
    """try_mark 통과 → delete_by_store 호출 → 로그."""

    async def test_deletes_existing_row_and_returns_true(
        self, handler, msg, valid_payload,
        store_payment_info_mock, processed_event_repo_mock, mock_logger,
    ):
        store_payment_info_mock.delete_by_store.return_value = True

        await handler.handle(msg)

        store_payment_info_mock.delete_by_store.assert_awaited_once_with(
            valid_payload["store_id"],
        )
        # try_mark 호출 인자 정확성 검증.
        processed_event_repo_mock.try_mark.assert_awaited_once()
        kw = processed_event_repo_mock.try_mark.await_args.kwargs
        assert kw["topic"] == TOPIC
        assert isinstance(kw["event_id"], UUID)

        # info 로그에 deleted=True 가 포함되는지.
        info_calls = [c for c in mock_logger.info.call_args_list]
        assert any(
            "deleted=" in str(c) and "True" in str(c.args)
            for c in info_calls
        ), f"deleted=True 로그 없음: {info_calls}"


    async def test_no_op_when_row_missing_returns_false(
        self,
        handler, msg, store_payment_info_mock, mock_logger,
    ):
        """이미 삭제된 store — delete_by_store 가 False 반환해도 정상 처리 (멱등)."""
        store_payment_info_mock.delete_by_store.return_value = False

        # raise 안 함.
        await handler.handle(msg)

        store_payment_info_mock.delete_by_store.assert_awaited_once()
        info_calls = mock_logger.info.call_args_list
        assert any(
            "deleted=" in str(c) and "False" in str(c.args)
            for c in info_calls
        ), f"deleted=False 로그 없음: {info_calls}"


@pytest.mark.unit
class TestDedupe:
    """try_mark False → delete 호출 / 핵심 로그 안 나옴."""

    async def test_skips_delete_when_try_mark_false(
        self, handler, msg,
        processed_event_repo_mock, store_payment_info_mock, mock_logger,
    ):
        processed_event_repo_mock.try_mark.return_value = False

        await handler.handle(msg)

        # 핵심: delete_by_store 호출 안 함 — 중복 적용 방지.
        store_payment_info_mock.delete_by_store.assert_not_awaited()
        # 중복 skip info 로그는 나옴, 그러나 "처리" 로그는 없어야.
        all_info = " ".join(str(c) for c in mock_logger.info.call_args_list)
        assert "중복" in all_info or "skip" in all_info.lower()
        assert "SellerStoreWithdrawn 처리" not in all_info


@pytest.mark.unit
class TestValidation:
    """파싱/검증 실패 → TerminalEventError → Runner 가 DLQ 격리."""

    async def test_raises_terminal_on_payload_field_missing(
        self, handler, make_msg, fixed_event_id,
        store_payment_info_mock,
    ):
        # store_id 누락
        bad_msg = make_msg(
            event_id=fixed_event_id,
            payload={"seller_email": "only_email@x.com"},
        )

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)

        store_payment_info_mock.delete_by_store.assert_not_awaited()


    async def test_raises_terminal_on_payload_none(
        self, handler, make_msg, fixed_event_id,
        store_payment_info_mock,
    ):
        """consumer value_deserializer 가 None 반환하는 케이스 (empty value)."""
        bad_msg = make_msg(event_id=fixed_event_id, payload=None)

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)

        store_payment_info_mock.delete_by_store.assert_not_awaited()


    async def test_raises_terminal_when_event_id_header_missing(
        self, handler, make_msg, valid_payload,
        store_payment_info_mock,
    ):
        bad_msg = make_msg(event_id=None, payload=valid_payload)

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)

        store_payment_info_mock.delete_by_store.assert_not_awaited()


    async def test_raises_terminal_when_event_id_not_uuid(
        self, handler, make_msg, valid_payload,
        store_payment_info_mock,
    ):
        bad_msg = make_msg(event_id="not-a-uuid", payload=valid_payload)

        with pytest.raises(TerminalEventError):
            await handler.handle(bad_msg)

        store_payment_info_mock.delete_by_store.assert_not_awaited()


@pytest.mark.unit
class TestServicePropagation:
    """서비스 예외는 catch 하지 않고 그대로 raise — Runner 가 retry/DLQ 결정."""

    async def test_propagates_delete_by_store_exception(
        self, handler, msg, store_payment_info_mock,
    ):
        store_payment_info_mock.delete_by_store.side_effect = RuntimeError(
            "DB transient",
        )

        with pytest.raises(RuntimeError, match="DB transient"):
            await handler.handle(msg)


    async def test_propagates_try_mark_exception(
        self, handler, msg, processed_event_repo_mock,
        store_payment_info_mock,
    ):
        processed_event_repo_mock.try_mark.side_effect = RuntimeError(
            "DB transient",
        )

        with pytest.raises(RuntimeError, match="DB transient"):
            await handler.handle(msg)

        # try_mark 실패 시 delete 호출되지 않음.
        store_payment_info_mock.delete_by_store.assert_not_awaited()
