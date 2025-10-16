import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from collections import defaultdict

from database.session import get_db
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.store_operation_info import StoreOperationInfoRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from schemas.order import OrderStatus
from services.payment import PaymentService
from services.email import email_service


logger = logging.getLogger(__name__)

# KST 타임존 설정
KST = timezone(timedelta(hours=9))


class AutoCancelReservationOrdersTask:
    """픽업 마감 시간(pickup_end_time)에 reservation 상태 주문을 취소하고 환불하는 스케줄 작업"""

    # 픽업 마감을 스케줄링 등록하기 위한 리스트
    _registered_job_ids: List[str] = []

    @staticmethod
    async def cancel_and_refund_store_reservation_orders(store_id: str, store_name: str):
        """특정 가게의 reservation 상태 주문을 취소하고 환불 처리"""
        logger.info(f"[{store_name}] 픽업 마감 - reservation 주문 자동 취소/환불 시작...")
        start_time = datetime.now(timezone.utc)

        cancelled_count = 0
        error_count = 0
        total_refund_amount = 0

        try:
            async for session in get_db():
                order_repo = OrderCurrentItemRepository(session)
                payment_info_repo = StorePaymentInfoRepository(session)
                
                payment_info = await payment_info_repo.get_by_store_id(store_id)

                if not payment_info or not payment_info.portone_secret_key:
                    logger.error(f"[{store_name}] 결제 설정이 없어 환불 처리 불가")
                    return

                all_orders = await order_repo.get_store_current_orders_with_relations(store_id)

                reservation_orders = [
                    order for order in all_orders
                    if order.status == OrderStatus.reservation
                ]

                if not reservation_orders:
                    logger.info(f"[{store_name}] 취소/환불 처리할 reservation 주문이 없습니다")
                    return

                # 각 주문을 취소하고 환불 처리
                for order in reservation_orders:
                    try:
                        refund_result = await PaymentService.process_refund(
                            payment_id=order.payment_id,
                            secret_key=payment_info.portone_secret_key,
                            reason="픽업 마감 시간 종료로 인한 자동 환불"
                        )

                        if refund_result.get("success"):
                            await order_repo.cancel_order(
                                payment_id=order.payment_id,
                                cancel_reason="픽업 마감 시간 종료로 인한 자동 환불"
                            )
                            
                            if email_service.is_configured():
                                email_service.send_template(
                                    recipient_email=order.customer_id,
                                    store_name=store_name,
                                    template_type="seller_cancel"
                                )
                            
                            cancelled_count += 1
                            total_refund_amount += order.total_amount

                            logger.info(
                                f"[{store_name}] 주문 자동 취소/환불 완료 - "
                                f"주문ID: {order.payment_id}, "
                                f"고객: {order.customer_id}, "
                                f"상품: {order.product.product_name}, "
                                f"금액: {order.total_amount:,}원"
                            )
                        else:
                            error_count += 1
                            logger.error(
                                f"[{store_name}] 주문 {order.payment_id} 환불 실패: "
                                f"{refund_result.get('error', '알 수 없는 오류')}"
                            )

                    except Exception as e:
                        error_count += 1
                        logger.error(
                            f"[{store_name}] 주문 {order.payment_id} 취소/환불 처리 중 오류: {str(e)}"
                        )

                # 작업 완료 통계
                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"[{store_name}] 픽업 마감 주문 자동 취소/환불 처리 완료: "
                    f"성공 {cancelled_count}건, 실패 {error_count}건, "
                    f"총 환불 금액 {total_refund_amount:,}원 "
                    f"(소요시간: {elapsed_time:.2f}초)"
                )

        except Exception as e:
            logger.error(f"[{store_name}] 주문 자동 취소/환불 처리 중 오류 발생: {e}", exc_info=True)

    @staticmethod
    async def register_daily_schedules(scheduler):
        """매일 새벽 5시에 실행: 오늘의 모든 가게 픽업 마감 시간 스케줄 등록"""
        logger.info("=== 픽업 마감 시간 동적 스케줄 등록 시작 ===")
        start_time = datetime.now(timezone.utc)

        try:
            AutoCancelReservationOrdersTask._remove_existing_jobs(scheduler)

            async for session in get_db():
                operation_repo = StoreOperationInfoRepository(session)

                now_kst = datetime.now(KST)
                today_day_of_week = now_kst.weekday()

                logger.info(
                    f"KST 기준 - 현재: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}, "
                    f"오늘 요일: {today_day_of_week}"
                )

                all_operations = await operation_repo.get_many(
                    filters={
                        "day_of_week": today_day_of_week,
                        "is_open_enabled": True
                    }
                )

                if not all_operations:
                    logger.info("오늘 운영하는 가게가 없습니다")
                    return

                stores_by_pickup_end_time = defaultdict(list)
                for operation in all_operations:
                    pickup_end_time_key = operation.pickup_end_time.strftime("%H:%M")
                    stores_by_pickup_end_time[pickup_end_time_key].append(operation)

                logger.info(
                    f"총 {len(all_operations)}개 가게, "
                    f"{len(stores_by_pickup_end_time)}개의 서로 다른 픽업 마감 시간"
                )

                registered_count = 0
                for pickup_end_time_str, operations in stores_by_pickup_end_time.items():
                    for operation in operations:
                        try:
                            job_id = f"auto_cancel_refund_{operation.store_id}_{today_day_of_week}"

                            run_datetime = datetime.combine(
                                now_kst.date(),
                                operation.pickup_end_time
                            ).replace(tzinfo=KST)

                            if run_datetime <= now_kst:
                                logger.debug(
                                    f"[{operation.store.store_name}] 픽업 마감 시간({pickup_end_time_str})이 "
                                    f"이미 지나 스케줄 등록 생략"
                                )
                                continue

                            scheduler.scheduler.add_job(
                                func=lambda sid=operation.store_id, sname=operation.store.store_name: \
                                    AutoCancelReservationOrdersTask.cancel_and_refund_store_reservation_orders(
                                        sid, sname
                                    ),
                                trigger='date',
                                run_date=run_datetime,
                                id=job_id,
                                name=f"[{operation.store.store_name}] 픽업 마감 시 주문 자동 취소/환불",
                                misfire_grace_time=1800,  # 30분 유예
                                replace_existing=True
                            )

                            AutoCancelReservationOrdersTask._registered_job_ids.append(job_id)
                            registered_count += 1

                            logger.info(
                                f"[{operation.store.store_name}] 스케줄 등록 완료 - "
                                f"픽업 마감: {pickup_end_time_str}, "
                                f"실행예정: {run_datetime.strftime('%Y-%m-%d %H:%M:%S KST')}"
                            )

                        except Exception as e:
                            logger.error(
                                f"[{operation.store.store_name}] 스케줄 등록 실패: {str(e)}",
                                exc_info=True
                            )

                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"=== 픽업 마감 동적 스케줄 등록 완료: {registered_count}개 작업 등록됨 "
                    f"(소요시간: {elapsed_time:.2f}초) ==="
                )

        except Exception as e:
            logger.error(f"동적 스케줄 등록 중 오류 발생: {e}", exc_info=True)

    @staticmethod
    def _remove_existing_jobs(scheduler):
        """기존에 등록된 동적 작업들 삭제"""
        removed_count = 0
        for job_id in AutoCancelReservationOrdersTask._registered_job_ids:
            try:
                scheduler.scheduler.remove_job(job_id)
                removed_count += 1
            except Exception:
                # 작업이 이미 실행되었거나 없는 경우 무시
                pass

        AutoCancelReservationOrdersTask._registered_job_ids.clear()

        if removed_count > 0:
            logger.info(f"기존 픽업 마감 동적 스케줄 {removed_count}개 삭제됨")

    @staticmethod
    async def force_cancel_refund_now(store_id: str) -> Dict[str, Any]:
        """수동으로 특정 가게의 주문을 즉시 취소/환불 처리 (테스트/관리 목적)"""
        logger.info(f"수동 주문 취소/환불 처리 요청됨 - 가게 ID: {store_id}")

        try:
            await AutoCancelReservationOrdersTask.cancel_and_refund_store_reservation_orders(
                store_id, f"가게_{store_id}"
            )
            return {
                "success": True,
                "message": f"가게 {store_id}의 주문 취소/환불 처리가 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 주문 취소/환불 처리 실패: {e}")
            return {
                "success": False,
                "message": f"주문 취소/환불 처리 실패: {str(e)}"
            }


# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": None,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 50,
    },
    "job_id": "register_auto_cancel_refund_schedules",
    "job_name": "픽업 마감 시간 동적 스케줄 등록 (취소/환불)",
    "misfire_grace_time": 3600,
}