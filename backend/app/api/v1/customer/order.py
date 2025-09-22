from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.string_utils import parse_comma_separated_string
from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    OrderCurrentItemRepositoryDep,
    StoreProductInfoRepositoryDep,
    StorePaymentInfoRepositoryDep
)
from repositories.store_product_info import StockUpdateResult
from schemas.order import (
    OrderItemResponse,
    OrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse,
    CustomerPickupCompleteRequest
)
from schemas.order import OrderStatus
from services.payment import PaymentService
from config.settings import settings
from utils.qr_generator import validate_qr_data

router = APIRouter(prefix="/orders", tags=["Customer-Order"])


@router.get("", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_order_history(
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    주문 내역 조회 - 모든 주문 조회
    """
    
    # 사용자의 모든 주문 조회
    orders = await order_repo.get_user_orders_with_relations(current_user["sub"])
    
    # response 포맷으로 변환
    order_responses = []
    for order in orders:
        order_response = OrderItemResponse(
            payment_id=order.payment_id,
            product_id=order.product_id,
            product_name=order.product.product_name,
            store_id=order.product.store_id,
            store_name=order.product.store.store_name,
            quantity=order.quantity,
            price=order.price,
            sale=order.sale,
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
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/today", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_current_orders(
    current_user: CurrentCustomerDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    당일 주문 조회
    """
    
    # 당일 주문 조회
    orders = await order_repo.get_user_current_orders_with_relations(current_user["sub"])
    
    # response 포맷으로 변환
    order_responses = []
    for order in orders:
        order_response = OrderItemResponse(
            payment_id=order.payment_id,
            product_id=order.product_id,
            product_name=order.product.product_name,
            store_id=order.product.store_id,
            store_name=order.product.store.store_name,
            quantity=order.quantity,
            price=order.price,
            sale=order.sale,
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
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses)
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
        product_id=order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=order.quantity,
        price=order.price,
        sale=order.sale,
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
    payment_info_repo: StorePaymentInfoRepositoryDep
):
    """
    주문 취소 (포트원 환불 포함)
    """
    
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
    
    return OrderCancelResponse(
        payment_id=payment_id,
        refunded_amount=order.price
    )


@router.patch("/{payment_id}/pickup-complete", response_model=OrderItemResponse,
    responses=create_error_responses({
        400:["유효하지 않은 QR 코드", "권한이 없는 사용자", "이미 픽업 완료"],
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
        current_user["sub"]
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # 세 가지 유저 ID 검증
    # 1. JWT의 유저 ID: current_user["sub"]
    # 2. QR의 유저 ID: qr_data["user_id"]
    # 3. 주문의 유저 ID: order.user_id
    
    if not (current_user["sub"] == qr_data["user_id"] == order.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="권한이 없는 사용자입니다"
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
        product_id=completed_order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=completed_order.quantity,
        price=completed_order.price,
        sale=order.sale,
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