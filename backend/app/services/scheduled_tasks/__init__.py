"""
uncompleted_order_refund_task : 미완료 주문 자동 환불 처리 스케줄링 / 4시
product_stock_update_task : 상품 재고 세팅값 업데이트 스케줄링 / 4시 5분
inventory_reset_task : 상품 재고 초기화 스케줄링 / 4시 10분
order_migration_task : 오늘 주문 테이블 -> 히스토리 테이블로 옮기는 스케줄링 / 4시 15분
store_operation_modification_apply_tasak : 가게 운영 정보 변경 스케줄링 / 4시 20분
store_operation_status_update_task : 가게 운영 상태 업데이트 / 4시 25분
store_auto_complete_order_task, AutoCancelReservationOrdersTask : 픽업 마감 시, 주문 취소 및 환불 스케줄링 등록 / 4시 30분
store_auto_cancel_reservation_order_task, AutoCompleteOrdersTask : 가게 마감 시, 주문 승인 스케줄링 등록 / 4시 35분
user_withdraw_process_task : 사용자 탈퇴 처리 스케줄링 / 4시 40분
"""
from .order_migration import scheduled_task as order_migration_task, OrderMigrationTask
from .product_stock_update import scheduled_task as product_stock_update_task, ProductStockUpdateTask
from .inventory_reset import scheduled_task as inventory_reset_task, InventoryResetTask
from .uncompleted_order_refund import scheduled_task as uncompleted_order_refund_task, UncompletedOrderRefundTask
from .operation_modification_apply import scheduled_task as operation_modification_apply_task, OperationModificationApplyTask
from .store_operation_status_update import scheduled_task as store_operation_status_update_task, StoreOperationStatusUpdateTask
from .auto_complete_orders import scheduled_task as store_auto_complete_order_task, AutoCompleteOrdersTask
from .auto_cancel_reservation_orders import scheduled_task as store_auto_cancel_reservation_order_task, AutoCancelReservationOrdersTask
from .user_withdraw_process import scheduled_task as user_withdraw_process_task, UserWithdrawProcessTask

__all__ = [
    'order_migration_task',
    'inventory_reset_task',
    'uncompleted_order_refund_task',
    'store_operation_status_update_task',
    'operation_modification_apply_task',
    'store_auto_complete_order_task',
    'store_auto_cancel_reservation_order_task',
    'user_withdraw_process_task',
    'product_stock_update_task',
    'OrderMigrationTask',
    'InventoryResetTask',
    'UncompletedOrderRefundTask',
    'StoreOperationStatusUpdateTask',
    'OperationModificationApplyTask',
    'AutoCompleteOrdersTask',
    'AutoCancelReservationOrdersTask',
    'UserWithdrawProcessTask',
    'ProductStockUpdateTask'
]