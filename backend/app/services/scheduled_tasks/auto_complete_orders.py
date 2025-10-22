import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from collections import defaultdict

from database.session import get_session
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.store_operation_info import StoreOperationInfoRepository
from schemas.order import OrderStatus


logger = logging.getLogger(__name__)

# KST 타임존 설정
KST = timezone(timedelta(hours=9))


class AutoCompleteOrdersTask:
    """가게 마감 시간(close_time)에 accept 상태 주문을 complete로 자동 변경하는 스케줄 작업"""

    # 가게 마감을 스케줄링 등록하기 위한 리스트
    _registered_job_ids: List[str] = []

    @staticmethod
    async def complete_store_accepted_orders(store_id: str, store_name: str):
        """특정 가게의 accept 상태 주문을 complete로 변경"""
        logger.info(f"[{store_name}] 가게 마감 - accept 주문 자동 완료 시작...")
        start_time = datetime.now(timezone.utc)

        completed_count = 0
        error_count = 0

        try:
            async with get_session() as session:
                order_repo = OrderCurrentItemRepository(session)

                all_orders = await order_repo.get_store_current_orders_with_relations(store_id)

                accepted_orders = [
                    order for order in all_orders
                    if order.status == OrderStatus.accept
                ]

                if not accepted_orders:
                    logger.info(f"[{store_name}] 완료 처리할 accept 주문이 없습니다")
                    return

                for order in accepted_orders:
                    try:
                        await order_repo.complete_order(order.payment_id)
                        completed_count += 1

                        logger.info(
                            f"[{store_name}] 주문 자동 완료 - "
                            f"주문ID: {order.payment_id}, "
                            f"고객: {order.customer_id}, "
                            f"상품: {order.product.product_name}"
                        )
                    except Exception as e:
                        error_count += 1
                        logger.error(
                            f"[{store_name}] 주문 {order.payment_id} 완료 처리 실패: {str(e)}"
                        )

                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"[{store_name}] 가게 마감 주문 자동 완료 처리 완료: "
                    f"성공 {completed_count}건, 실패 {error_count}건 "
                    f"(소요시간: {elapsed_time:.2f}초)"
                )

        except Exception as e:
            logger.error(f"[{store_name}] 주문 자동 완료 처리 중 오류 발생: {e}", exc_info=True)

    @staticmethod
    async def register_daily_schedules(scheduler):
        """매일 새벽 5시에 실행: 오늘의 모든 가게 마감 시간 스케줄 등록"""
        logger.info("=== 가게 마감 시간 동적 스케줄 등록 시작 ===")
        start_time = datetime.now(timezone.utc)

        try:
            # 기존에 등록된 스케줄링 작업들 삭제 (시간이 바뀔 수도 있어서)
            AutoCompleteOrdersTask._remove_existing_jobs(scheduler)

            async with get_session(auto_commit=False) as session:
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
                    },
                    load_relations=["store"]
                )

                if not all_operations:
                    logger.info("오늘 운영하는 가게가 없습니다")
                    return

                # 가게 마감 시간 별로 가게 그룹화
                stores_by_close_time = defaultdict(list)
                for operation in all_operations:
                    close_time_key = operation.close_time.strftime("%H:%M")
                    stores_by_close_time[close_time_key].append(operation)

                logger.info(f"총 {len(all_operations)}개 가게, {len(stores_by_close_time)}개의 서로 다른 마감 시간")

                # 각 마감 시간별로 스케줄 등록
                registered_count = 0
                for close_time_str, operations in stores_by_close_time.items():
                    for operation in operations:
                        try:
                            job_id = f"auto_complete_{operation.store_id}_{today_day_of_week}"

                            # 오늘 날짜 + close_time으로 정확한 실행 시간 계산
                            run_datetime = datetime.combine(
                                now_kst.date(),
                                operation.close_time
                            ).replace(tzinfo=KST)

                            # 이미 지난 시간이면 등록하지 않음
                            if run_datetime <= now_kst:
                                logger.debug(
                                    f"[{operation.store.store_name}] 마감 시간({close_time_str})이 "
                                    f"이미 지나 스케줄 등록 생략"
                                )
                                continue

                            store_name = operation.store.store_name
                            scheduler.scheduler.add_job(
                                func=lambda sid=operation.store_id, sname=store_name: \
                                    AutoCompleteOrdersTask.complete_store_accepted_orders(sid, sname),
                                trigger='date',
                                run_date=run_datetime,
                                id=job_id,
                                name=f"[{store_name}] 마감 시 주문 자동 완료",
                                misfire_grace_time=1800,  # 30분 유예
                                replace_existing=True
                            )

                            AutoCompleteOrdersTask._registered_job_ids.append(job_id)
                            registered_count += 1

                            logger.info(
                                f"[{operation.store.store_name}] 스케줄 등록 완료 - "
                                f"마감시간: {close_time_str}, "
                                f"실행예정: {run_datetime.strftime('%Y-%m-%d %H:%M:%S KST')}"
                            )

                        except Exception as e:
                            logger.error(
                                f"[{operation.store.store_name}] 스케줄 등록 실패: {str(e)}",
                                exc_info=True
                            )

                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"=== 동적 스케줄 등록 완료: {registered_count}개 작업 등록됨 "
                    f"(소요시간: {elapsed_time:.2f}초) ==="
                )

        except Exception as e:
            logger.error(f"동적 스케줄 등록 중 오류 발생: {e}", exc_info=True)

    @staticmethod
    def _remove_existing_jobs(scheduler):
        """기존에 등록된 동적 작업들 삭제"""
        removed_count = 0
        for job_id in AutoCompleteOrdersTask._registered_job_ids:
            try:
                scheduler.scheduler.remove_job(job_id)
                removed_count += 1
            except Exception:
                # 작업이 이미 실행되었거나 없는 경우 무시
                pass

        AutoCompleteOrdersTask._registered_job_ids.clear()

        if removed_count > 0:
            logger.info(f"기존 동적 스케줄 {removed_count}개 삭제됨")

    @staticmethod
    async def force_complete_now(store_id: str) -> Dict[str, Any]:
        """수동으로 특정 가게의 주문을 즉시 완료 처리 (테스트/관리 목적)"""
        logger.info(f"수동 주문 완료 처리 요청됨 - 가게 ID: {store_id}")

        try:
            await AutoCompleteOrdersTask.complete_store_accepted_orders(store_id, f"가게_{store_id}")
            return {
                "success": True,
                "message": f"가게 {store_id}의 주문 완료 처리가 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 주문 완료 처리 실패: {e}")
            return {
                "success": False,
                "message": f"주문 완료 처리 실패: {str(e)}"
            }


# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": None,
    "trigger": "cron",
    "trigger_args": {
        "hour": 5,
        "minute": 0,
    },
    "job_id": "register_auto_complete_schedules",
    "job_name": "가게 마감 시간 동적 스케줄 등록",
    "misfire_grace_time": 3600,
}