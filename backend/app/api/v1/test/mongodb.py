from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from repositories.order_history_item import OrderHistoryItemRepository
from database.mongodb_models.order_history_item import OrderHistoryItem

router = APIRouter(
    prefix="/mongodb/order-history",
    responses={404: {"description": "Not found"}},
)


# Test DTOs
class CreateOrderHistoryRequest(BaseModel):
    payment_id: str = Field(..., description="구매 고유 ID")
    product_id: str = Field(..., description="상품 고유 ID")
    customer_id: str = Field(..., description="유저 고유 ID")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    total_amount: int = Field(..., description="최종 금액")
    status: str = Field(default="reservation", description="상태")
    preferred_menus: Optional[str] = Field(None, description="유저의 선호 메뉴 (콤마로 구분)")
    nutrition_types: Optional[str] = Field(None, description="식품 영양 타입 (콤마로 구분)")
    allergies: Optional[str] = Field(None, description="알레르기/제약조건 (콤마로 구분)")
    topping_types: Optional[str] = Field(None, description="선호 토핑 (콤마로 구분)")


class OrderHistoryResponse(BaseModel):
    id: str
    payment_id: str
    product_id: str
    customer_id: str
    quantity: int
    price: int
    sale: Optional[int]
    total_amount: int
    status: str
    reservation_at: datetime
    accepted_at: Optional[datetime]
    completed_at: Optional[datetime]
    canceled_at: Optional[datetime]
    cancel_reason: Optional[str]
    preferred_menus: Optional[str]
    nutrition_types: Optional[str]
    allergies: Optional[str]
    topping_types: Optional[str]
    created_at: datetime
    updated_at: datetime


# Repository 인스턴스
order_history_repo = OrderHistoryItemRepository()


@router.post("", response_model=OrderHistoryResponse, summary="주문 히스토리 생성")
async def create_order_history(
    request: CreateOrderHistoryRequest
):
    """테스트용 주문 히스토리 생성"""
    try:
        # OrderHistoryItem 생성
        order_history = OrderHistoryItem(
            payment_id=request.payment_id,
            product_id=request.product_id,
            customer_id=request.customer_id,
            quantity=request.quantity,
            price=request.price,
            sale=request.sale,
            total_amount=request.total_amount,
            status=request.status,
            preferred_menus=request.preferred_menus,
            nutrition_types=request.nutrition_types,
            allergies=request.allergies,
            topping_types=request.topping_types,
            reservation_at=datetime.now(timezone.utc)
        )
        
        # DB에 저장
        saved_item = await order_history_repo.create(order_history)
        
        return OrderHistoryResponse(
            id=str(saved_item.id),
            payment_id=saved_item.payment_id,
            product_id=saved_item.product_id,
            customer_id=saved_item.customer_id,
            quantity=saved_item.quantity,
            price=saved_item.price,
            sale=saved_item.sale,
            total_amount=saved_item.total_amount,
            status=saved_item.status,
            reservation_at=saved_item.reservation_at,
            accepted_at=saved_item.accepted_at,
            completed_at=saved_item.completed_at,
            canceled_at=saved_item.canceled_at,
            cancel_reason=saved_item.cancel_reason,
            preferred_menus=saved_item.preferred_menus,
            nutrition_types=saved_item.nutrition_types,
            allergies=saved_item.allergies,
            topping_types=saved_item.topping_types,
            created_at=saved_item.created_at,
            updated_at=saved_item.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment/{payment_id}", response_model=OrderHistoryResponse, summary="결제 ID로 조회")
async def get_order_history_by_payment_id(
    payment_id: str
):
    """결제 ID로 주문 히스토리 조회"""
    order_history = await order_history_repo.get_by_payment_id(payment_id)
    
    if not order_history:
        raise HTTPException(status_code=404, detail="Order history not found")
    
    return OrderHistoryResponse(
        id=str(order_history.id),
        payment_id=order_history.payment_id,
        product_id=order_history.product_id,
        customer_id=order_history.customer_id,
        quantity=order_history.quantity,
        price=order_history.price,
        sale=order_history.sale,
        total_amount=order_history.total_amount,
        status=order_history.status,
        reservation_at=order_history.reservation_at,
        accepted_at=order_history.accepted_at,
        completed_at=order_history.completed_at,
        canceled_at=order_history.canceled_at,
        cancel_reason=order_history.cancel_reason,
        preferred_menus=order_history.preferred_menus,
        nutrition_types=order_history.nutrition_types,
        allergies=order_history.allergies,
        topping_types=order_history.topping_types,
        created_at=order_history.created_at,
        updated_at=order_history.updated_at
    )


@router.get("/product/{product_id}", response_model=OrderHistoryResponse, summary="상품 ID로 조회")
async def get_order_history_by_payment_id(
    product_id: str
):
    """상품 ID로 주문 히스토리 조회"""
    order_history = await order_history_repo.get_by_product_id(product_id)
    
    if not order_history:
        raise HTTPException(status_code=404, detail="Order history not found")
    
    return OrderHistoryResponse(
        id=str(order_history.id),
        payment_id=order_history.payment_id,
        product_id=order_history.product_id,
        customer_id=order_history.customer_id,
        quantity=order_history.quantity,
        price=order_history.price,
        sale=order_history.sale,
        total_amount=order_history.total_amount,
        status=order_history.status,
        reservation_at=order_history.reservation_at,
        accepted_at=order_history.accepted_at,
        completed_at=order_history.completed_at,
        canceled_at=order_history.canceled_at,
        cancel_reason=order_history.cancel_reason,
        preferred_menus=order_history.preferred_menus,
        nutrition_types=order_history.nutrition_types,
        allergies=order_history.allergies,
        topping_types=order_history.topping_types,
        created_at=order_history.created_at,
        updated_at=order_history.updated_at
    )


@router.get("/customer/{customer_id}", response_model=List[OrderHistoryResponse], summary="사용자 주문 히스토리")
async def get_customer_order_history(
    customer_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 10
):
    """특정 사용자의 주문 히스토리 조회"""
    histories = await order_history_repo.get_customer_history(
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return [
        OrderHistoryResponse(
            id=str(history.id),
            payment_id=history.payment_id,
            product_id=history.product_id,
            customer_id=history.customer_id,
            quantity=history.quantity,
            price=history.price,
            sale=history.sale,
            total_amount=history.total_amount,
            status=history.status,
            reservation_at=history.reservation_at,
            accepted_at=history.accepted_at,
            completed_at=history.completed_at,
            canceled_at=history.canceled_at,
            cancel_reason=history.cancel_reason,
            preferred_menus=history.preferred_menus,
            nutrition_types=history.nutrition_types,
            allergies=history.allergies,
            topping_types=history.topping_types,
            created_at=history.created_at,
            updated_at=history.updated_at
        )
        for history in histories
    ]


@router.get("/statistics/daily", summary="일별 주문 통계")
async def get_daily_statistics(
    date: datetime
):
    """특정 날짜의 주문 통계 조회"""
    summary = await order_history_repo.get_daily_summary(date)
    return summary


@router.get("/statistics/monthly/{year}/{month}", summary="월별 주문 통계")
async def get_monthly_statistics(
    year: int,
    month: int
):
    """월별 주문 통계 조회"""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid month")
    
    statistics = await order_history_repo.get_monthly_statistics(year, month)
    return statistics


@router.post("/bulk-archive", summary="주문 일괄 아카이브")
async def bulk_archive_orders(
    orders: List[CreateOrderHistoryRequest]
):
    """여러 주문을 일괄적으로 아카이브"""
    orders_data = [order.model_dump() for order in orders]
    count = await order_history_repo.bulk_archive_orders(orders_data)
    
    return {"archived_count": count, "message": f"Successfully archived {count} orders"}


@router.get("/search/preferences", response_model=List[OrderHistoryResponse], summary="선호도 기준 검색")
async def search_by_preferences(
    preferred_menus: Optional[str] = None,
    nutrition_types: Optional[str] = None,
    allergies: Optional[str] = None
):
    """선호도 기준으로 주문 히스토리 검색"""
    # 콤마로 구분된 문자열을 리스트로 변환
    preferred_menus_list = preferred_menus.split(",") if preferred_menus else None
    nutrition_types_list = nutrition_types.split(",") if nutrition_types else None
    allergies_list = allergies.split(",") if allergies else None
    
    histories = await order_history_repo.search_by_preferences(
        preferred_menus=preferred_menus_list,
        nutrition_types=nutrition_types_list,
        allergies=allergies_list
    )
    
    return [
        OrderHistoryResponse(
            id=str(history.id),
            payment_id=history.payment_id,
            product_id=history.product_id,
            customer_id=history.customer_id,
            quantity=history.quantity,
            price=history.price,
            sale=history.sale,
            total_amount=history.total_amount,
            status=history.status,
            reservation_at=history.reservation_at,
            accepted_at=history.accepted_at,
            completed_at=history.completed_at,
            canceled_at=history.canceled_at,
            cancel_reason=history.cancel_reason,
            preferred_menus=history.preferred_menus,
            nutrition_types=history.nutrition_types,
            allergies=history.allergies,
            topping_types=history.topping_types,
            created_at=history.created_at,
            updated_at=history.updated_at
        )
        for history in histories
    ]


@router.post("/test-data/generate", summary="테스트 데이터 생성")
async def generate_test_data(
    count: int = 10
):
    """테스트용 더미 데이터 생성"""
    if count > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 records at once")
    
    created_items = []
    
    for i in range(count):
        order_history = OrderHistoryItem(
            payment_id=f"PAY_{datetime.now().timestamp()}_{i}",
            product_id=f"PROD_{i % 5}",  # 5개 상품으로 순환
            customer_id=f"Customer_{i % 3}",  # 3명의 사용자로 순환
            quantity=(i % 3) + 1,
            price=10000 + (i * 1000),
            sale=10 if i % 2 == 0 else None,
            total_amount=(10000 + (i * 1000)) * ((i % 3) + 1) * (0.9 if i % 2 == 0 else 1),
            status="completed" if i % 3 == 0 else "reservation",
            preferred_menus="김밥,떡볶이" if i % 2 == 0 else "햄버거,피자",
            nutrition_types="고단백,저탄수화물" if i % 3 == 0 else "균형잡힌",
            allergies="땅콩" if i % 5 == 0 else None,
            topping_types="치즈,베이컨" if i % 2 == 0 else "야채",
            reservation_at=datetime.now(timezone.utc) - timedelta(days=i)
        )
        
        if i % 3 == 0:
            order_history.completed_at = order_history.reservation_at + timedelta(hours=1)
        
        created_item = await order_history_repo.create(order_history)
        created_items.append(created_item)
    
    return {
        "created_count": len(created_items),
        "message": f"Successfully created {len(created_items)} test records"
    }