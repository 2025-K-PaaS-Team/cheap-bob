import enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class OrderStatus(enum.Enum):
    reservation = "reservation" # 예약 중
    accept = "accept" # 주문 수락
    complete = "complete" # 픽업 완료
    cancel = "cancel" # 취소
    
class OrderItemResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    customer_id: str = Field(..., description="소비자 고유 ID")
    customer_nickname: str = Field(..., description="소비자 이름")
    customer_phone_number: str = Field(..., description="소비자 핸드폰 번호")
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    total_amount: int = Field(..., description="총 결제 금액")
    status: OrderStatus = Field(..., description="주문 상태")
    reservation_at: datetime = Field(..., description="예약 주문 시간")
    accepted_at: Optional[datetime] = Field(None, description="주문 수락 시간")
    completed_at: Optional[datetime] = Field(None, description="픽업 완료 시간")
    canceled_at: Optional[datetime] = Field(None, description="주문 취소 시간")
    cancel_reason: Optional[str] = Field(None, description="취소 사유")
    preferred_menus: Optional[List[str]] = Field(default=None, description="소비자의 선호 메뉴")
    nutrition_types: Optional[List[str]] = Field(default=None, description="식품 영양 타입")
    allergies: Optional[List[str]] = Field(default=None, description="알레르기/제약조건")
    topping_types: Optional[List[str]] = Field(default=None, description="선호 토핑")
    
    class Config:
        from_attributes = True
        
class OrderListResponse(BaseModel):
    orders: List[OrderItemResponse] = Field(default_factory=list, description="주문 목록")
    total: int = Field(..., description="전체 주문 수")

class CustomerOrderItemResponse(OrderItemResponse):
    main_image_url: Optional[str] = Field(None, description="대표 이미지 URL")
        
class CustomerOrderListResponse(BaseModel):
    orders: List[CustomerOrderItemResponse] = Field(default_factory=list, description="주문 목록")
    total: int = Field(..., description="전체 주문 수")
    
class CustomerTodayOrderItemResponse(CustomerOrderItemResponse):
    pickup_start_time: str = Field(..., description="가게 픽업 시작 시간 (HH:MM)")
    pickup_end_time: str = Field(..., description="픽업 종료 시간 (HH:MM)")
        
class CustomerTodayOrderListResponse(BaseModel):
    orders: List[CustomerTodayOrderItemResponse] = Field(default_factory=list, description="주문 목록")
    total: int = Field(..., description="전체 주문 수")

class OrderCancelRequest(BaseModel):
    reason: str = Field(default="‘요청’ 으로 주문이 취소되었어요.", description="환불 사유", min_length=1, max_length=255)


class OrderCancelResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    total_amount: int = Field(..., description="총 결제 금액")
    

class CustomerPickupCompleteRequest(BaseModel):
    qr_data: str = Field(..., description="QR 코드 데이터")


class SellerPickupQRResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    qr_data: str = Field(..., description="QR 코드 데이터")
    created_at: datetime = Field(..., description="QR 생성 시간")


class DashboardStockItem(BaseModel):
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    current_stock: int = Field(..., description="현재 남아있는 재고 수량")
    initial_stock: int = Field(..., description="설정된 최초 재고 수량")
    purchased_stock: int = Field(..., description="현재까지 구매된 수량 (수락 전 + 수락 + 완료 - 취소)")
    adjustment_stock: int = Field(..., description="관리자가 설정한 총 재고 수량")
    
    class Config:
        from_attributes = True
        

class DashboardResponse(BaseModel):
    items: List[DashboardStockItem] = Field(default_factory=list, description="상품별 재고 현황")
    total_items: int = Field(..., description="전체 상품 수")


class SettlementItem(BaseModel):
    product_name: str = Field(..., description="상품 이름")
    quantity: int = Field(..., description="판매된 개수")
    total_amount: int = Field(..., description="최종 판매가")
    status: OrderStatus = Field(..., description="주문 상태 (complete/cancel)")
    time_at: str = Field(..., description="시간 (HH:MM)")


class SettlementDayGroup(BaseModel):
    date: str = Field(..., description="날짜 KST (YYYY-MM-DD)")
    items: List[SettlementItem] = Field(default_factory=list, description="해당 날짜의 정산 아이템들")


class SettlementResponse(BaseModel):
    daily_settlements: List[SettlementDayGroup] = Field(default_factory=list, description="날짜별 정산 데이터")


class WeeklyRevenueResponse(BaseModel):
    total_revenue: int = Field(..., description="월요일부터 오늘까지의 총 수익")


class TodayAlarmOrderCard(BaseModel):
    """오늘의 알림용 주문 카드"""
    payment_id: str = Field(..., description="결제 고유 ID")
    order_time: datetime = Field(..., description="주문 상태별 시간")
    quantity: int = Field(..., description="상품 수량")
    price: int = Field(..., description="상품 가격 (원)")
    sale: Optional[int] = Field(None, description="상품 세일 정보 (퍼센트)")
    total_amount: int = Field(..., description="최종 결제 금액")
    status: OrderStatus = Field(..., description="주문 상태")
    store_name: str = Field(..., description="가게 이름")
    product_name: str = Field(..., description="상품 명")
    pickup_start_time: str = Field(..., description="가게 픽업 시작 시간 (HH:MM)")
    pickup_end_time: str = Field(..., description="픽업 종료 시간 (HH:MM)")

    class Config:
        from_attributes = True


class TodayAlarmResponse(BaseModel):
    """오늘의 알림 응답"""
    alarm_cards: List[TodayAlarmOrderCard] = Field(default_factory=list, description="알림 카드 목록")
    total: int = Field(..., description="전체 알림 개수")
