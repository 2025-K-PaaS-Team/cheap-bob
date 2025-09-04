"""
StorePaymentInfo와 OrderHistoryItem Repository 사용 예시
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import (
    StorePaymentInfoRepository,
    OrderHistoryItemRepository,
    OrderCurrentItemRepository
)
from schemas.order import OrderStatus


# 1. 가게 결제 정보 관리
async def manage_store_payment_info(db: AsyncSession):
    payment_repo = StorePaymentInfoRepository(db)
    
    # 결제 정보 생성
    payment_info = await payment_repo.create(
        store_id="STORE001",
        portone_store_id="portone_123",
        portone_channel_id="channel_456",
        portone_secret_key="secret_789"
    )
    
    # 결제 정보 조회
    info = await payment_repo.get_by_store_id("STORE001")
    
    # 결제 정보 완전성 확인
    is_complete = await payment_repo.has_complete_info("STORE001")
    print(f"결제 정보 완전성: {is_complete}")
    
    # 포트원 정보 업데이트
    updated = await payment_repo.update_portone_info(
        store_id="STORE001",
        portone_channel_id="new_channel_789"
    )


# 2. 주문 내역 조회
async def query_order_history(db: AsyncSession):
    history_repo = OrderHistoryItemRepository(db)
    
    # 사용자별 주문 내역
    user_orders = await history_repo.get_by_user_id(
        user_id="USER001",
        status=OrderStatus.accepted,
        limit=10
    )
    
    # 날짜 범위로 조회
    today = datetime.now(timezone.utc)
    last_week = today - timedelta(days=7)
    
    weekly_orders = await history_repo.get_by_date_range(
        start_date=last_week,
        end_date=today,
        user_id="USER001"
    )
    
    # 사용자 통계
    user_stats = await history_repo.get_user_statistics("USER001")
    print(f"총 주문: {user_stats['total_orders']}")
    print(f"완료 주문: {user_stats['completed_orders']}")
    print(f"총 지출: {user_stats['total_spent']:,}원")


# 3. 주문 상태 관리
async def manage_order_status(db: AsyncSession):
    history_repo = OrderHistoryItemRepository(db)
    
    # 예약 주문 생성
    order = await history_repo.create(
        payment_id="PAY001",
        product_id="PROD001",
        user_id="USER001",
        quantity=2,
        price=5000,
        status=OrderStatus.reservation
    )
    
    # 주문 수락 (예제 - 실제로는 order_current_item에서 사용)
    # accepted = await current_repo.accept_order("PAY001")
    
    # 주문 취소 (예약 상태일 때만 가능)
    canceled = await history_repo.cancel_order("PAY002")


# 4. 상품 판매 통계
async def product_sales_analytics(db: AsyncSession):
    history_repo = OrderHistoryItemRepository(db)
    
    # 상품별 판매 통계
    sales_stats = await history_repo.get_product_sales_history("PROD001")
    
    print(f"총 판매 수: {sales_stats['total_orders']}")
    print(f"총 판매량: {sales_stats['total_quantity_sold']}")
    print(f"총 매출: {sales_stats['total_revenue']:,}원")
    print(f"평균 판매가: {sales_stats['average_price']:,}원")


# 5. 일일 마감 - 당일 주문을 히스토리로 이동
async def daily_closing(db: AsyncSession):
    current_repo = OrderCurrentItemRepository(db)
    history_repo = OrderHistoryItemRepository(db)
    
    # 당일 모든 주문 조회
    today_orders = await current_repo.delete_all_items()
    
    # 히스토리로 마이그레이션
    if today_orders:
        order_data = []
        for order in today_orders:
            order_data.append({
                "payment_id": order.payment_id,
                "product_id": order.product_id,
                "user_id": order.user_id,
                "quantity": order.quantity,
                "price": order.price,
                "status": order.status,
                "order_time": order.order_time
            })
        
        history_items = await history_repo.migrate_from_current_orders(order_data)
        print(f"{len(history_items)}개의 주문이 히스토리로 이동되었습니다")


# 6. 복합 조회 예시
async def complex_queries(db: AsyncSession):
    history_repo = OrderHistoryItemRepository(db)
    payment_repo = StorePaymentInfoRepository(db)
    
    # 결제 정보가 있는 가게들만 조회
    stores_with_payment = await payment_repo.get_many(
        filters={"portone_store_id": {"not": None}},
        load_relations=["store"]
    )
    
    # 특정 기간 내 취소된 주문들
    last_month = datetime.now(timezone.utc) - timedelta(days=30)
    canceled_orders = await history_repo.get_by_date_range(
        start_date=last_month,
        end_date=datetime.now(timezone.utc),
        status=OrderStatus.cancel
    )
    
    print(f"지난 30일간 취소된 주문: {len(canceled_orders)}건")