import logging
from datetime import datetime, timezone
from typing import Dict, Any
from collections import defaultdict

from database.session import get_db
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from schemas.order import OrderStatus
from services.payment import PaymentService


logger = logging.getLogger(__name__)


class UncompletedOrderRefundTask:
    """미완료 주문(reservation, accept 상태)을 환불 처리하는 스케줄 작업"""
    
    @staticmethod
    async def refund_uncompleted_orders():
        """당일 미완료 주문을 환불 처리하는 메인 로직"""
        logger.info("미완료 주문 환불 처리 작업 시작...")
        start_time = datetime.now(timezone.utc)
        
        refund_count = 0
        error_count = 0
        total_refund_amount = 0
        
        try:
            async for session in get_db():
                order_repo = OrderCurrentItemRepository(session)
                payment_info_repo = StorePaymentInfoRepository(session)
                
                # reservation과 accept 상태의 모든 주문 조회
                all_orders = await order_repo.get_all_orders_with_relations()
                uncompleted_orders = [
                    order for order in all_orders 
                    if order.status in [OrderStatus.reservation, OrderStatus.accept]
                ]
                
                if not uncompleted_orders:
                    logger.info("환불 처리할 미완료 주문이 없습니다")
                    return
                
                # 가게별로 주문을 그룹화
                orders_by_store = defaultdict(list)
                for order in uncompleted_orders:
                    store_id = order.product.store_id
                    orders_by_store[store_id].append(order)
                
                # 가게별로 환불 처리
                for store_id, store_orders in orders_by_store.items():

                    payment_info = await payment_info_repo.get_by_store_id(store_id)
                    
                    if not payment_info or not payment_info.portone_secret_key:
                        logger.error(f"가게 {store_id}의 결제 설정이 없어 {len(store_orders)}개 주문 환불 실패")
                        error_count += len(store_orders)
                        continue
                    
                    for order in store_orders:
                        try:
                            # 포트원 환불 처리
                            refund_result = await PaymentService.process_refund(
                                payment_id=order.payment_id,
                                secret_key=payment_info.portone_secret_key,
                                reason="영업 시간 종료로 인한 자동 환불"
                            )
                            
                            if refund_result.get("success"):
                                # 주문 취소 처리
                                quantity = await order_repo.cancel_order(
                                    payment_id=order.payment_id,
                                    cancel_reason="영업 시간 종료로 인한 자동 환불"
                                )
                                
                                refund_count += 1
                                total_refund_amount += order.total_amount
                                
                                logger.info(
                                    f"주문 {order.payment_id} 환불 완료 - "
                                    f"고객: {order.customer_id}, "
                                    f"상품: {order.product.product_name}, "
                                    f"금액: {order.total_amount:,}원"
                                )
                            else:
                                error_count += 1
                                logger.error(
                                    f"주문 {order.payment_id} 환불 실패: "
                                    f"{refund_result.get('error', '알 수 없는 오류')}"
                                )
                                
                        except Exception as e:
                            error_count += 1
                            logger.error(f"주문 {order.payment_id} 환불 처리 중 오류: {str(e)}")
                
                # 작업 완료 통계
                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"미완료 주문 환불 처리 완료: "
                    f"성공 {refund_count}건, 실패 {error_count}건, "
                    f"총 환불 금액 {total_refund_amount:,}원 "
                    f"(소요시간: {elapsed_time:.2f}초)"
                )
                
                UncompletedOrderRefundTask._log_refund_statistics(
                    refund_count, error_count, total_refund_amount
                )
                
        except Exception as e:
            logger.error(f"미완료 주문 환불 처리 중 오류 발생: {e}", exc_info=True)
    
    @staticmethod
    def _log_refund_statistics(refund_count: int, error_count: int, total_amount: int):
        """환불 통계 로깅"""
        logger.info(
            f"환불 처리 통계 - "
            f"성공: {refund_count}건, "
            f"실패: {error_count}건, "
            f"총 환불 금액: {total_amount:,}원, "
            f"처리 시각: {datetime.now(timezone.utc).isoformat()}"
        )
    
    @staticmethod
    async def force_refund_now() -> Dict[str, Any]:
        """수동으로 즉시 환불 처리 실행 (테스트/관리 목적)"""
        logger.info("수동 미완료 주문 환불 처리 요청됨")
        
        try:
            await UncompletedOrderRefundTask.refund_uncompleted_orders()
            return {
                "success": True,
                "message": "미완료 주문 환불 처리가 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 환불 처리 실패: {e}")
            return {
                "success": False,
                "message": f"환불 처리 실패: {str(e)}"
            }

# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": UncompletedOrderRefundTask.refund_uncompleted_orders,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 0,
    },
    "job_id": "refund_uncompleted_orders",
    "job_name": "미완료 주문 자동 환불 처리",
    "misfire_grace_time": 3600,  # 1시간의 유예 시간
}