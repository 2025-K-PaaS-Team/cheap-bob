"""PaymentRefundCompletedEventHandler 단위 테스트.

핵심 검증:
  - quantity 양수 → cancel + restore_stock + 이메일 발송.
  - quantity 0 → restore_stock + 이메일 모두 skip (race 흡수 케이스).
  - 중복 event_id → 즉시 skip (dedupe).
"""
import pytest


@pytest.mark.unit
class TestNormalCancel:
    """주문이 reservation/accept 상태 → cancel_order 가 quantity 양수 반환."""

    async def test_cancels_restores_stock_and_sends_email(
        self, handler, msg, v2_payload,
        order_repo_mock, seller_product_mock, send_email_mock,
    ):
        order_repo_mock.cancel_order.return_value = 2

        await handler.handle(msg)

        order_repo_mock.cancel_order.assert_awaited_once_with(
            v2_payload["payment_id"], v2_payload["reason"],
        )
        seller_product_mock.restore_purchased_stock.assert_awaited_once_with(
            product_id=v2_payload["product_id"], quantity=2,
        )
        send_email_mock.assert_awaited_once_with(
            v2_payload["customer_id"], v2_payload["store_name"],
        )


@pytest.mark.unit
class TestRaceAbsorption:
    """수동 cancel 흐름이 이미 처리 → cancel_order quantity=0 → restore/이메일 skip.

    race fix 의 핵심 — 중복 이메일/재고 복원 방지.
    """

    async def test_skips_stock_restore_and_email_when_already_cancelled(
        self, handler, msg,
        order_repo_mock, seller_product_mock, send_email_mock,
    ):
        # 다른 흐름 (수동 cancel) 이 이미 처리 — quantity 0.
        order_repo_mock.cancel_order.return_value = 0

        await handler.handle(msg)

        # cancel_order 호출 자체는 됨 (idempotent).
        order_repo_mock.cancel_order.assert_awaited_once()
        # 그러나 restore + 이메일 모두 skip.
        seller_product_mock.restore_purchased_stock.assert_not_awaited()
        send_email_mock.assert_not_awaited()


@pytest.mark.unit
class TestDedupe:
    """중복 event_id 메시지 재배달 → 즉시 skip (DB/이메일 모두 건드리지 않음)."""

    async def test_dedupe_skips_all_side_effects(
        self, handler, msg,
        processed_event_repo_mock,
        order_repo_mock, seller_product_mock, send_email_mock,
    ):
        processed_event_repo_mock.try_mark.return_value = False

        await handler.handle(msg)

        order_repo_mock.cancel_order.assert_not_awaited()
        seller_product_mock.restore_purchased_stock.assert_not_awaited()
        send_email_mock.assert_not_awaited()


@pytest.mark.unit
class TestEmailFailureDoesNotRollback:
    """이메일 발송 실패 — DB cancel 은 이미 commit 됐으므로 영향 없음.

    tx 안에서 이메일 보내면 외부 IO 가 tx rollback 영향 — 그래서 tx 밖 best-effort 패턴.
    """

    async def test_email_failure_swallowed(
        self, handler, msg,
        order_repo_mock, seller_product_mock, send_email_mock,
    ):
        order_repo_mock.cancel_order.return_value = 2
        send_email_mock.side_effect = RuntimeError("SMTP down")

        # raise 안 함 — caller (Runner) 가 보면 정상 처리.
        await handler.handle(msg)

        # DB 부수효과는 그대로 적용.
        seller_product_mock.restore_purchased_stock.assert_awaited_once()
