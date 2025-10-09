from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import pytz

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email

from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep,
    OrderCurrentItemRepositoryDep,
    OrderHistoryItemRepositoryDep
)
from schemas.order import (
    OrderStatus,
    SettlementResponse,
    SettlementDayGroup,
    SettlementItem,
    WeeklyRevenueResponse
)

router = APIRouter(prefix="/store/settlement", tags=["Seller-Settlement"])
kst = pytz.timezone('Asia/Seoul')

@router.get("", response_model=SettlementResponse,
    responses=create_error_responses({
        400:"날짜 범위가 올바르지 않음",
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })
)
async def get_store_settlement(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    history_repo: OrderHistoryItemRepositoryDep,
    start_date: datetime = Query(..., description="조회 시작일"),
    end_date: datetime = Query(..., description="조회 시작일")
):
    """
    가게 정산 조회
    - start_date와 end_date 기간의 정산 데이터를 조회합니다
    - complete와 cancel 상태의 주문만 포함됩니다
    - 날짜별로 그룹화하여 반환합니다
    """
    
    seller_email = current_user["sub"]
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    # 날짜 유효성 검증
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작일이 종료일보다 늦을 수 없습니다"
        )
    
    # 현재 시간 (KST)
    today = datetime.now(kst).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 프론트에서 받은 KST 날짜를 UTC로 변환
    start_date_kst = kst.localize(start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None))
    start_date_utc = start_date_kst.astimezone(pytz.UTC)
    
    end_date_kst = kst.localize(end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=None))
    end_date_utc = end_date_kst.astimezone(pytz.UTC)
    
    all_orders = []
    
    # end_date가 오늘인 경우 current에서 조회
    if end_date_kst.date() >= today.date():
        current_orders = await order_repo.get_store_orders_with_relations(store_id)
        
        for order in current_orders:
            # 날짜 범위 체크 (UTC 기준)
            if order.status in [OrderStatus.complete, OrderStatus.cancel]:
                
                # UTC를 KST로 변환
                kst_time = order.reservation_at.astimezone(kst)
                
                all_orders.append({
                    'product_name': order.product.product_name,
                    'quantity': order.quantity,
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'date': kst_time.date()
                })
    
    # 과거 날짜가 포함된 경우 history에서 조회
    if start_date_kst.date() < today.date():
        history_orders = await history_repo.get_store_history(
            store_id=store_id,
            start_date=start_date_utc,
            end_date=end_date_utc
        )
        
        # 상태 필터링
        for order in history_orders:
            if order.status in ["complete", "cancel"]:
                # UTC를 KST로 변환
                kst_time = order.reservation_at.astimezone(kst)
                
                all_orders.append({
                    'product_name': order.product_name,
                    'quantity': order.quantity,
                    'total_amount': order.total_amount,
                    'status': OrderStatus[order.status],
                    'date': kst_time.date()
                })
    
    # 날짜별로 그룹화
    daily_data: Dict[str, List[Dict]] = defaultdict(list)
    for order in all_orders:
        date_str = order['date'].strftime('%Y-%m-%d')
        daily_data[date_str].append(order)
    
    daily_settlements = []
    
    for date_str in sorted(daily_data.keys()):
        orders = daily_data[date_str]
        items = []
        for order in orders:
            items.append(SettlementItem(
                product_name=order['product_name'],
                quantity=order['quantity'],
                total_amount=order['total_amount'],
                status=order['status']
            ))
        
        daily_settlements.append(SettlementDayGroup(
            date=date_str,
            items=items,
        ))
    
    return SettlementResponse(
        daily_settlements=daily_settlements
    )


@router.get("/weekly-revenue", response_model=WeeklyRevenueResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })
)
async def get_weekly_revenue(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    history_repo: OrderHistoryItemRepositoryDep
):
    """
    주간 수익 집계
    - 월요일부터 오늘까지의 complete 상태 주문의 총 수익을 반환합니다
    """
    
    seller_email = current_user["sub"]
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    today_kst = datetime.now(kst)
    
    # 이번 주 월요일 찾기
    days_since_monday = today_kst.weekday()
    monday_kst = (today_kst - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    monday_utc = monday_kst.astimezone(pytz.UTC)
    
    total_revenue = 0
    
    # 오늘 날짜의 주문은 current에서 조회
    current_orders = await order_repo.get_store_orders_with_relations(store_id)
    
    for order in current_orders:
        if order.status == OrderStatus.complete:
            total_revenue += order.total_amount
    
    # 월요일부터 어제까지의 주문은 history에서 조회
    if days_since_monday > 0:
        yesterday_end_utc = (today_kst - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.UTC)
        
        history_orders = await history_repo.get_store_history(
            store_id=store_id,
            start_date=monday_utc,
            end_date=yesterday_end_utc
        )
        
        for order in history_orders:
            if order.status == "complete":
                total_revenue += order.total_amount
    
    return WeeklyRevenueResponse(
        total_revenue=total_revenue
    )