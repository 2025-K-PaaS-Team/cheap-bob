import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from database.session import get_db
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.order_history_item import OrderHistoryItemRepository


logger = logging.getLogger(__name__)


class OrderMigrationTask:
    """주문 데이터를 현재 테이블에서 히스토리 테이블로 마이그레이션하는 스케줄 작업"""
    
    @staticmethod
    async def migrate_current_orders_to_history():
        """당일 주문을 히스토리로 이동하는 메인 로직"""
        logger.info("주문 마이그레이션 시작...")
        start_time = datetime.now(timezone.utc)
        
        try:
            async for session in get_db():
                current_order_repo = OrderCurrentItemRepository(session)
                history_order_repo = OrderHistoryItemRepository()
                
                # 먼저 관계 정보를 포함하여 모든 주문을 조회
                all_current_orders = await current_order_repo.get_all_orders_with_relations()
                
                if not all_current_orders:
                    logger.info("마이그레이션할 주문이 없습니다")
                    return
                
                orders_data = []
                for order in all_current_orders:
                    order_dict = {
                        "payment_id": order.payment_id,
                        "customer_id": order.customer_id,
                        "customer_nickname": order.customer.detail.nickname,
                        "customer_phone_number": order.customer.detail.phone_number,
                        "product_id": order.product_id,
                        "product_name": order.product.product_name,
                        "store_id": order.product.store_id,
                        "store_name": order.product.store.store_name,
                        "quantity": order.quantity,
                        "price": order.price,
                        "sale": order.sale,
                        "total_amount": order.total_amount,
                        "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
                        "reservation_at": order.reservation_at,
                        "accepted_at": order.accepted_at,
                        "completed_at": order.completed_at,
                        "canceled_at": order.canceled_at,
                        "cancel_reason": order.cancel_reason,
                        "preferred_menus": order.preferred_menus,
                        "nutrition_types": order.nutrition_types,
                        "allergies": order.allergies,
                        "topping_types": order.topping_types
                    }
                    orders_data.append(order_dict)
                
                # 데이터 저장 후 삭제
                archived_count = await history_order_repo.bulk_archive_orders(orders_data)
                
                # 저장이 성공한 후에만 삭제
                await current_order_repo.delete_all_items()
                
                elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(
                    f"주문 마이그레이션 완료: "
                    f"{archived_count}개의 주문이 히스토리로 이동됨 "
                    f"(소요시간: {elapsed_time:.2f}초)"
                )
                
                OrderMigrationTask._log_migration_statistics(orders_data)
                
        except Exception as e:
            logger.error(f"주문 마이그레이션 중 오류 발생: {e}", exc_info=True)
    
    @staticmethod
    def _log_migration_statistics(orders_data: List[Dict[str, Any]]):
        """마이그레이션 통계 로깅"""
        if not orders_data:
            return
        
        status_counts = {}
        total_revenue = 0
        
        for order in orders_data:
            status = order.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            total_revenue += order.get("total_amount", 0)
        
        logger.info(
            f"마이그레이션 통계 - "
            f"총 주문수: {len(orders_data)}, "
            f"총 매출: {total_revenue:,}원, "
            f"상태별: {status_counts}"
        )
    
    @staticmethod
    async def force_migrate_now() -> Dict[str, Any]:
        """수동으로 즉시 마이그레이션 실행 (테스트/관리 목적)"""
        logger.info("수동 마이그레이션 요청됨")
        
        try:
            await OrderMigrationTask.migrate_current_orders_to_history()
            return {
                "success": True,
                "message": "마이그레이션이 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 마이그레이션 실패: {e}")
            return {
                "success": False,
                "message": f"마이그레이션 실패: {str(e)}"
            }

# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": OrderMigrationTask.migrate_current_orders_to_history,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 10,
    },
    "job_id": "migrate_daily_orders",
    "job_name": "당일 주문을 히스토리로 이동",
    "misfire_grace_time": 3600,  # 1시간의 유예 시간
}