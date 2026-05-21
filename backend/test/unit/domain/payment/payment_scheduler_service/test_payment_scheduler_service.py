"""Tests for ``app.domain.payment.service.payment_scheduler.PaymentSchedulerService``."""
from datetime import datetime, timedelta
from types import SimpleNamespace
import pytest


# ────────────────────────────────────────────────────────────────────
# schedule_payment_timeout
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestSchedulePaymentTimeout:

    async def test_registers_job_with_correct_id(self, service, scheduler_mock):
        ok = await service.schedule_payment_timeout(
            payment_id="PAY_x", product_id="PRD_y", quantity=2,
        )

        assert ok is True
        scheduler_mock.add_job.assert_called_once()
        kwargs = scheduler_mock.add_job.call_args.kwargs
        assert kwargs["id"] == "payment_timeout_PAY_x"
        assert kwargs["trigger"] == "date"
        assert kwargs["replace_existing"] is True
        # 5분 후 ± 약간 오차 안에서 등록됐는지 확인.
        run_date: datetime = kwargs["run_date"]
        delta = run_date - datetime.now(run_date.tzinfo)
        assert timedelta(minutes=4, seconds=30) <= delta <= timedelta(minutes=5, seconds=30)


    async def test_returns_false_when_apscheduler_raises(self, service, scheduler_mock):
        scheduler_mock.add_job.side_effect = RuntimeError("scheduler down")
        ok = await service.schedule_payment_timeout(
            payment_id="PAY_x", product_id="PRD_y", quantity=1,
        )
        assert ok is False


    async def test_timeout_callback_restores_stock_and_deletes_cart(
        self, service, scheduler_mock, product_service_mock, order_query_mock,
    ):
        """add_job 에 넘긴 콜백을 직접 실행해 sideeffects 확인."""
        await service.schedule_payment_timeout(
            payment_id="PAY_x", product_id="PRD_y", quantity=4,
        )

        callback = scheduler_mock.add_job.call_args.kwargs["func"]
        await callback()

        product_service_mock.restore_purchased_stock.assert_awaited_once_with(
            product_id="PRD_y", quantity=4,
        )
        order_query_mock.delete_cart_item.assert_awaited_once_with("PAY_x")


    async def test_timeout_callback_swallows_restore_failure(
        self, service, scheduler_mock, product_service_mock, order_query_mock,
    ):
        """재고 복구 실패가 cart 삭제를 막아선 안 된다 (logger.error + 진행)."""
        await service.schedule_payment_timeout(
            payment_id="PAY_x", product_id="PRD_y", quantity=4,
        )
        product_service_mock.restore_purchased_stock.side_effect = RuntimeError("db err")

        callback = scheduler_mock.add_job.call_args.kwargs["func"]
        await callback()  # 예외가 propagate 되어선 안 된다.

        order_query_mock.delete_cart_item.assert_awaited_once_with("PAY_x")


# ────────────────────────────────────────────────────────────────────
# remove_payment_schedule
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestRemovePaymentSchedule:

    def test_returns_false_when_no_job(self, service, scheduler_mock):
        scheduler_mock.get_job.return_value = None
        assert service.remove_payment_schedule("PAY_x") is False
        scheduler_mock.remove_job.assert_not_called()


    def test_removes_job_and_returns_true(self, service, scheduler_mock):
        scheduler_mock.get_job.return_value = SimpleNamespace(id="payment_timeout_PAY_x")
        assert service.remove_payment_schedule("PAY_x") is True
        scheduler_mock.remove_job.assert_called_once_with("payment_timeout_PAY_x")


    def test_returns_false_when_remove_raises(self, service, scheduler_mock):
        scheduler_mock.get_job.return_value = SimpleNamespace(id="x")
        scheduler_mock.remove_job.side_effect = RuntimeError("boom")
        assert service.remove_payment_schedule("PAY_x") is False
