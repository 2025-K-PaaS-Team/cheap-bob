from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from datetime import datetime, timezone, timedelta

from utils.qr_generator import validate_qr_data
from utils.docs_error import create_error_responses
from utils.string_utils import parse_comma_separated_string
from utils.store_utils import get_main_image_url
from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    OrderCurrentItemRepositoryDep,
    OrderHistoryItemRepositoryDep,
    StoreProductInfoRepositoryDep,
    StorePaymentInfoRepositoryDep,
    StoreRepositoryDep,
    StoreImageRepositoryDep
)
from repositories.store_product_info import StockUpdateResult
from schemas.order import (
    OrderStatus,
    OrderItemResponse,
    CustomerOrderItemResponse,
    CustomerOrderListResponse,
    CustomerTodayOrderItemResponse,
    CustomerTodayOrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse,
    CustomerPickupCompleteRequest,
    TodayAlarmOrderCard,
    TodayAlarmResponse
)
from services.payment import PaymentService
from services.background_email import send_customer_cancel_email
from config.settings import settings

# KST 타임존 설정
KST = timezone(timedelta(hours=9))

router = APIRouter(prefix="/orders", tags=["Customer-Order"])


@router.get("", response_model=CustomerOrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_order_history(
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep,
    history_repo: OrderHistoryItemRepositoryDep,
    image_repo: StoreImageRepositoryDep
):
    """
    주문 내역 조회 - 모든 주문 조회 (당일 + 과거)
    """
    customer_email = current_user["sub"]
    
    # 당일 주문 조회
    current_orders = await order_repo.get_customer_current_orders(customer_email)
    
    # 과거 주문 조회
    history_orders = await history_repo.get_customer_history(customer_email)
    
    order_responses = []
    
    # 당일 주문 처리
    for order in current_orders:
        order_response = CustomerOrderItemResponse(
            payment_id=order.payment_id,
            customer_id=order.customer_id,
            customer_nickname=order.customer.detail.nickname,
            customer_phone_number=order.customer.detail.phone_number,
            product_id=order.product_id,
            product_name=order.product.product_name,
            store_id=order.product.store_id,
            store_name=order.product.store.store_name,
            main_image_url=get_main_image_url(order.product.store),
            quantity=order.quantity,
            price=order.price,
            sale=order.sale,
            total_amount=order.total_amount,
            status=order.status,
            reservation_at=order.reservation_at,
            accepted_at=order.accepted_at,
            completed_at=order.completed_at,
            canceled_at=order.canceled_at,
            cancel_reason=order.cancel_reason,
            preferred_menus=parse_comma_separated_string(order.preferred_menus),
            nutrition_types=parse_comma_separated_string(order.nutrition_types),
            allergies=parse_comma_separated_string(order.allergies),
            topping_types=parse_comma_separated_string(order.topping_types)
        )
        order_responses.append(order_response)
    
    history_store_ids = list(set(order.store_id for order in history_orders))
    
    store_main_images = await image_repo.get_main_images_for_stores(history_store_ids)
    
    # 과거 주문 처리
    for history_order in history_orders:
        
        main_image_url = store_main_images.get(history_order.store_id)
        
        order_response = CustomerOrderItemResponse(
            payment_id=history_order.payment_id,
            customer_id=history_order.customer_id,
            customer_nickname=history_order.customer_nickname,
            customer_phone_number=history_order.customer_phone_number,
            product_id=history_order.product_id,
            product_name=history_order.product_name,
            store_id=history_order.store_id,
            store_name=history_order.store_name,
            main_image_url=main_image_url,
            quantity=history_order.quantity,
            price=history_order.price,
            sale=history_order.sale,
            total_amount=history_order.total_amount,
            status=history_order.status,
            reservation_at=history_order.reservation_at.replace(tzinfo=None) if history_order.reservation_at and history_order.reservation_at.tzinfo else history_order.reservation_at,
            accepted_at=history_order.accepted_at.replace(tzinfo=None) if history_order.accepted_at and history_order.accepted_at.tzinfo else history_order.accepted_at,
            completed_at=history_order.completed_at.replace(tzinfo=None) if history_order.completed_at and history_order.completed_at.tzinfo else history_order.completed_at,
            canceled_at=history_order.canceled_at.replace(tzinfo=None) if history_order.canceled_at and history_order.canceled_at.tzinfo else history_order.canceled_at,
            cancel_reason=history_order.cancel_reason,
            preferred_menus=parse_comma_separated_string(history_order.preferred_menus),
            nutrition_types=parse_comma_separated_string(history_order.nutrition_types),
            allergies=parse_comma_separated_string(history_order.allergies),
            topping_types=parse_comma_separated_string(history_order.topping_types)
        )
        order_responses.append(order_response)
    
    order_responses.sort(
        key=lambda x: max(
            filter(None, [x.reservation_at, x.accepted_at, x.completed_at, x.canceled_at])
        ),
        reverse=True
    )
    
    return CustomerOrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/today", response_model=CustomerTodayOrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_order_today(
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    당일 주문 조회
    """
    customer_email = current_user["sub"]
    
    today = datetime.now(KST).weekday()
    
    orders = await order_repo.get_customer_current_orders_with_pickup_time(customer_email, today)
    
    order_responses = []
    
    for order in orders:
        
        pickup_start_time = order.product.store.today_operation_info.pickup_start_time.strftime("%H:%M")
        pickup_end_time = order.product.store.today_operation_info.pickup_end_time.strftime("%H:%M")
        
        order_response = CustomerTodayOrderItemResponse(
            payment_id=order.payment_id,
            customer_id=order.customer_id,
            customer_nickname=order.customer.detail.nickname,
            customer_phone_number=order.customer.detail.phone_number,
            product_id=order.product_id,
            product_name=order.product.product_name,
            store_id=order.product.store_id,
            store_name=order.product.store.store_name,
            main_image_url=get_main_image_url(order.product.store),
            quantity=order.quantity,
            price=order.price,
            sale=order.sale,
            total_amount=order.total_amount,
            status=order.status,
            reservation_at=order.reservation_at,
            accepted_at=order.accepted_at,
            completed_at=order.completed_at,
            canceled_at=order.canceled_at,
            cancel_reason=order.cancel_reason,
            preferred_menus=parse_comma_separated_string(order.preferred_menus),
            nutrition_types=parse_comma_separated_string(order.nutrition_types),
            allergies=parse_comma_separated_string(order.allergies),
            topping_types=parse_comma_separated_string(order.topping_types),
            pickup_start_time=pickup_start_time,
            pickup_end_time=pickup_end_time
        )
        order_responses.append(order_response)
    
    order_responses.sort(
        key=lambda x: max(
            filter(None, [x.reservation_at, x.accepted_at, x.completed_at, x.canceled_at])
        ),
        reverse=True
    )
    
    return CustomerTodayOrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/today-alarm", response_model=TodayAlarmResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_today_alarm(
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    당일 알림 조회
    """
    
    customer_email = current_user["sub"]
    
    today_weekday = datetime.now(KST).weekday()
    
    orders = await order_repo.get_today_alarm_orders(customer_email, today_weekday)
    
    alarm_cards = []
    
    for order in orders:
        
        pickup_start_time = order.product.store.today_operation_info.pickup_start_time.strftime("%H:%M")
        pickup_end_time = order.product.store.today_operation_info.pickup_end_time.strftime("%H:%M")
        
        # 기본 카드 정보
        base_card_info = {
            "payment_id": order.payment_id,
            "quantity": order.quantity,
            "price": order.price,
            "sale": order.sale,
            "total_amount": order.total_amount,
            "store_name": order.product.store.store_name,
            "product_name": order.product.product_name,
            "pickup_start_time": pickup_start_time,
            "pickup_end_time": pickup_end_time
        }
        
        if order.reservation_at:
            alarm_card = TodayAlarmOrderCard(
                **base_card_info,
                order_time=order.reservation_at,
                status=OrderStatus.reservation
            )
            alarm_cards.append(alarm_card)
        
        if order.accepted_at:
            alarm_card = TodayAlarmOrderCard(
                **base_card_info,
                order_time=order.accepted_at,
                status=OrderStatus.accept
            )
            alarm_cards.append(alarm_card)
        
        if order.canceled_at:
            alarm_card = TodayAlarmOrderCard(
                **base_card_info,
                order_time=order.canceled_at,
                status=OrderStatus.cancel
            )
            alarm_cards.append(alarm_card)
    
    alarm_cards.sort(key=lambda x: x.order_time, reverse=True)
    
    return TodayAlarmResponse(
        alarm_cards=alarm_cards,
        total=len(alarm_cards)
    )


@router.get("/{payment_id}", response_model=OrderItemResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404: "주문을 찾을 수 없음"
    })            
)
async def get_order_detail(
    payment_id: str,
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    주문 상세 정보 조회
    """
    
    # 주문 조회 (with product info)
    order = await order_repo.get_order_with_store_relation(payment_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    return OrderItemResponse(
        payment_id=order.payment_id,
        customer_id=order.customer_id,
        customer_nickname=order.customer.detail.nickname,
        customer_phone_number=order.customer.detail.phone_number,
        product_id=order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=order.quantity,
        price=order.price,
        sale=order.sale,
        total_amount=order.total_amount,
        status=order.status,
        reservation_at=order.reservation_at,
        accepted_at=order.accepted_at,
        completed_at=order.completed_at,
        canceled_at=order.canceled_at,
        cancel_reason=order.cancel_reason,
        preferred_menus=parse_comma_separated_string(order.preferred_menus),
        nutrition_types=parse_comma_separated_string(order.nutrition_types),
        allergies=parse_comma_separated_string(order.allergies),
        topping_types=parse_comma_separated_string(order.topping_types)
    )


@router.patch("/{payment_id}/complete", response_model=OrderItemResponse,
    responses=create_error_responses({
        400:["유효하지 않은 QR 코드", "권한이 없는 소비자", "이미 픽업 완료"],
        401:["인증 정보가 없음", "토큰 만료"],
        404:["주문을 찾을 수 없음", "QR 코드를 찾을 수 없음"]
    })               
)
async def complete_pickup(
    payment_id: str,
    request: CustomerPickupCompleteRequest,
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    픽업 완료 처리 (QR 코드 검증)
    """
    customer_email = current_user["sub"]
    
    # 주문 조회
    order = await order_repo.get_order_with_store_relation(payment_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 주문 상태 확인
    if order.status != OrderStatus.accept:
        if order.status == OrderStatus.complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 픽업이 완료된 주문입니다"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="주문이 수락되지 않았습니다"
            )
    
    # QR 데이터 검증
    is_valid, qr_data, error_msg = validate_qr_data(
        request.qr_data,
        customer_email
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # 세 가지 소비자 ID 검증
    # 1. JWT의 소비자 ID: customer_email
    # 2. QR의 소비자 ID: qr_data["customer_id"]
    # 3. 주문의 소비자 ID: order.customer_id
    
    if not (customer_email == qr_data["customer_id"] == order.customer_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="권한이 없는 소비자입니다"
        )
    
    # 결제 ID 검증
    if qr_data["payment_id"] != payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 QR 코드입니다"
        )
    
    # 상품 ID 검증
    if qr_data["product_id"] != order.product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="상품 정보가 일치하지 않습니다"
        )
    
    # 주문 상태를 완료로 변경
    completed_order = await order_repo.complete_order(payment_id)
    
    return OrderItemResponse(
        payment_id=completed_order.payment_id,
        customer_id=order.customer_id,
        customer_nickname=order.customer.detail.nickname,
        customer_phone_number=order.customer.detail.phone_number,
        product_id=completed_order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=completed_order.quantity,
        price=completed_order.price,
        sale=order.sale,
        total_amount=order.total_amount,
        status=completed_order.status,
        reservation_at=completed_order.reservation_at,
        accepted_at=completed_order.accepted_at,
        completed_at=completed_order.completed_at,
        canceled_at=order.canceled_at,
        cancel_reason=completed_order.cancel_reason,
        preferred_menus=parse_comma_separated_string(completed_order.preferred_menus),
        nutrition_types=parse_comma_separated_string(completed_order.nutrition_types),
        allergies=parse_comma_separated_string(completed_order.allergies),
        topping_types=parse_comma_separated_string(completed_order.topping_types)
    )
    
    
@router.delete("/{payment_id}/cancel", response_model=OrderCancelResponse,
    responses=create_error_responses({
        400: ["이미 취소된 주문", "이미 승인된 주문"],
        401:["인증 정보가 없음", "토큰 만료"],
        404:"상품을 찾을 수 없음",
        409: "동시성 충돌 발생"
    })               
)
async def cancel_order(
    payment_id: str,
    request: OrderCancelRequest,
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    payment_info_repo: StorePaymentInfoRepositoryDep,
    store_repo: StoreRepositoryDep,
    background_tasks: BackgroundTasks
):
    """
    주문 취소 (포트원 환불 포함)
    """
    customer_email = current_user["sub"]
    
    # 주문 조회 (with product info)
    order = await order_repo.get_order_with_product_relation(payment_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 이미 취소된 주문인지 확인
    if order.status == OrderStatus.cancel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 취소된 주문입니다"
        )
    
    # 수락된 주문은 취소 불가
    if order.status in [OrderStatus.accept, OrderStatus.complete]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리 중인 주문은 취소할 수 없습니다"
        )
    
    # 가게의 결제 정보 조회
    payment_info = await payment_info_repo.get_by_store_id(order.product.store_id)
    
    # 포트원 환불 처리
    refund_result = await PaymentService.process_refund(
        payment_id=payment_id,
        secret_key=payment_info.portone_secret_key,
        reason=request.reason
    )
    
    if not refund_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=refund_result.get("error", "환불 처리 중 오류가 발생했습니다")
        )
    
    # 주문 취소 처리
    quantity = await order_repo.cancel_order(payment_id, cancel_reason=request.reason)
 
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        result = await product_repo.adjust_purchased_stock(order.product_id, -quantity)
        
        if result == StockUpdateResult.SUCCESS:
            break
        
        if attempt == max_retries - 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="재고 복구 중 충돌이 발생했습니다. 다시 시도해주세요."
            )
    
    # 소비자 주문 취소 이메일을 백그라운드로 전송
    store = await store_repo.get_by_store_id(order.product.store_id)
    background_tasks.add_task(send_customer_cancel_email, customer_email, store.store_name)
    
    return OrderCancelResponse(
        payment_id=payment_id,
        quantity=order.quantity,
        price=order.price,
        sale=order.sale,
        total_amount=order.total_amount,
    )