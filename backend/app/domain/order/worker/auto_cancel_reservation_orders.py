"""픽업 마감 시간(pickup_end_time) 에 reservation 상태 주문을 취소/환불하는 스케줄 작업.

`register_daily_schedules` 가 매일 새벽에 fired 되어, 오늘 열려 있는 가게마다
픽업 마감 시각에 1회성 job 을 등록한다. 실제 비즈니스 로직은
`SellerOrderService.cancel_store_reservation_orders()` 에 위치.
"""
from typing import List
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from app.core.logger import get_logger
from app.container import container


logger = get_logger("order.worker.auto_cancel_reservation_orders")

KST = timezone(timedelta(hours=9))


class AutoCancelReservationOrdersTask:
    """픽업 마감 시간에 reservation 주문을 자동 취소/환불."""

    _registered_job_ids: List[str] = []

    @staticmethod
    async def cancel_and_refund_store_reservation_orders(
        store_id: str, store_name: str,
    ):
        """단일 가게의 reservation 주문 환불/취소/재고 복원."""
        start = datetime.now(timezone.utc)
        try:
            cancelled, failed, total_amount = await container.seller_order_service(
            ).cancel_store_reservation_orders(
                store_id=store_id,
                store_name=store_name,
                reason="‘조기 마감’ 으로 주문이 취소되었어요.",
            )
        except Exception:
            logger.exception(
                "[{}] 주문 자동 취소/환불 처리 중 오류 발생", store_name,
            )
            return

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            "[{}] 픽업 마감 주문 자동 취소/환불 완료: 성공 {}건, 실패 {}건, "
            "환불 {:,}원 ({:.2f}s)",
            store_name, cancelled, failed, total_amount, elapsed,
        )


    @staticmethod
    async def register_daily_schedules(scheduler):
        """매일 새벽 실행: 오늘 영업하는 모든 가게에 픽업 마감 시각 1회성 job 등록."""
        logger.info("=== 픽업 마감 시간 동적 스케줄 등록 시작 ===")
        start = datetime.now(timezone.utc)
        try:
            AutoCancelReservationOrdersTask._remove_existing_jobs(scheduler)

            now_kst = datetime.now(KST)
            today_dow = now_kst.weekday()
            logger.info(
                "KST 기준 - 현재: {}, 오늘 요일: {}",
                now_kst.strftime("%Y-%m-%d %H:%M:%S"), today_dow,
            )

            operations = await container.seller_store_settings_service(
            ).list_today_open_operations()
            if not operations:
                logger.info("오늘 운영하는 가게가 없습니다")
                return

            stores_by_pickup_end_time = defaultdict(list)
            for op in operations:
                key = op.pickup_end_time.strftime("%H:%M")
                stores_by_pickup_end_time[key].append(op)

            logger.info(
                "총 {}개 가게, {}개의 서로 다른 픽업 마감 시간",
                len(operations), len(stores_by_pickup_end_time),
            )

            registered = 0
            for pickup_end_time_str, ops in stores_by_pickup_end_time.items():
                for op in ops:
                    try:
                        job_id = (
                            f"auto_cancel_refund_{op.store_id}_{today_dow}"
                        )
                        run_dt = datetime.combine(
                            now_kst.date(), op.pickup_end_time,
                        ).replace(tzinfo=KST)
                        if run_dt <= now_kst:
                            logger.debug(
                                "[{}] 픽업 마감({})이 이미 지나 등록 생략",
                                op.store.store_name, pickup_end_time_str,
                            )
                            continue

                        store_name = op.store.store_name
                        scheduler.scheduler.add_job(
                            func=AutoCancelReservationOrdersTask.cancel_and_refund_store_reservation_orders,
                            trigger="date",
                            run_date=run_dt,
                            id=job_id,
                            name=f"[{store_name}] 픽업 마감 시 주문 자동 취소/환불",
                            misfire_grace_time=1800,
                            replace_existing=True,
                            args=[op.store_id, store_name],
                        )
                        AutoCancelReservationOrdersTask._registered_job_ids.append(
                            job_id,
                        )
                        registered += 1
                        logger.info(
                            "[{}] 스케줄 등록 - 픽업 마감: {}, 실행예정: {}",
                            store_name, pickup_end_time_str,
                            run_dt.strftime("%Y-%m-%d %H:%M:%S KST"),
                        )
                    except Exception:
                        logger.exception(
                            "[{}] 스케줄 등록 실패", op.store.store_name,
                        )

            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            logger.info(
                "=== 픽업 마감 동적 스케줄 등록 완료: {}개 작업 ({:.2f}s) ===",
                registered, elapsed,
            )
        except Exception:
            logger.exception("동적 스케줄 등록 중 오류 발생")


    @staticmethod
    def _remove_existing_jobs(scheduler):
        removed = 0
        for job_id in AutoCancelReservationOrdersTask._registered_job_ids:
            try:
                scheduler.scheduler.remove_job(job_id)
                removed += 1
            except Exception:
                pass
        AutoCancelReservationOrdersTask._registered_job_ids.clear()
        if removed > 0:
            logger.info("기존 픽업 마감 동적 스케줄 {}개 삭제됨", removed)


scheduled_task = {
    "func": None,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 30,
    },
    "job_id": "register_auto_cancel_refund_schedules",
    "job_name": "픽업 마감 시간 동적 스케줄 등록 (취소/환불)",
    "misfire_grace_time": 3600,
}
