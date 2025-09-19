from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from utils.qr_generator import encode_qr_data
from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from utils.string_utils import parse_comma_separated_string

from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep,
    OrderCurrentItemRepositoryDep,
    StoreProductInfoRepositoryDep,
    StorePaymentInfoRepositoryDep
)
from schemas.order import (
    OrderItemResponse,
    OrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse,
    OrderStatus,
    SellerPickupQRResponse
)
from services.payment import PaymentService
from config.settings import settings

router = APIRouter(prefix="/store/orders", tags=["Seller-Order"])


@router.get("", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })          
)
async def get_store_orders(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    가게의 주문 목록 조회
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    orders = await order_repo.get_store_orders_with_relations(store_id)
    
    order_responses = []
    for order in orders:
        order_response = OrderItemResponse(
            payment_id=order.payment_id,
            product_id=order.product_id,
            product_name=order.product.product_name,
            quantity=order.quantity,
            price=order.price,
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


@router.get("/pending", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })                 
)
async def get_pending_orders(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    처리 대기중인 주문 조회 (reservation, accepted, complete)
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    orders = await order_repo.get_store_pending_orders_with_relations(store_id)
    
    order_responses = []
    for order in orders:
        order_response = OrderItemResponse(
            payment_id=order.payment_id,
            product_id=order.product_id,
            product_name=order.product.product_name,
            quantity=order.quantity,
            price=order.price,
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


@router.patch("/{payment_id}/accept", response_model=OrderItemResponse,
    responses=create_error_responses({
        400:"이미 처리한 주문",
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })                   
)
async def update_order_accept(
    payment_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    주문 수락
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    order = await order_repo.get_order_with_product_relation(payment_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    if order.status != OrderStatus.reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 처리된 주문입니다"
        )
    
    updated_order = await order_repo.update(
        payment_id,
        status=OrderStatus.accept,
        accepted_at=datetime.now(timezone.utc)
    )
    
    # response 포맷으로 변환
    return OrderItemResponse(
        payment_id=updated_order.payment_id,
        product_id=updated_order.product_id,
        product_name=order.product.product_name,
        quantity=updated_order.quantity,
        price=updated_order.price,
        status=updated_order.status,
        reservation_at=updated_order.reservation_at,
        accepted_at=updated_order.accepted_at,
        completed_at=updated_order.completed_at,
        canceled_at=order.canceled_at,
        cancel_reason=updated_order.cancel_reason,
        preferred_menus=parse_comma_separated_string(updated_order.preferred_menus),
        nutrition_types=parse_comma_separated_string(updated_order.nutrition_types),
        allergies=parse_comma_separated_string(updated_order.allergies),
        topping_types=parse_comma_separated_string(updated_order.topping_types)
    )


@router.post("/{payment_id}/cancel", response_model=OrderCancelResponse,
    responses=create_error_responses({
        400:"이미 취소한 주문",
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음",
        409:"재고 복구 중, 충돌 발생"
    })                    
)
async def cancel_order(
    payment_id: str,
    request: OrderCancelRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    payment_info_repo: StorePaymentInfoRepositoryDep
):
    """
    주문 취소 (포트원 환불 포함)
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    order = await order_repo.get_order_with_product_relation(payment_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    if order.status == OrderStatus.cancel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 취소된 주문입니다"
        )
    
    # 가게의 결제 정보 조회
    payment_info = await payment_info_repo.get_by_store_id(store_id)
    if not payment_info or not payment_info.portone_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="가게의 결제 설정이 완료되지 않았습니다"
        )
    
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
    
    quantity = await order_repo.cancel_order(payment_id, cancel_reason=request.reason)
    
    # 재고 복구
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        try:
            current_product = await product_repo.get_by_product_id(order.product_id)
            
            success = await product_repo.update_lock(
                order.product_id,
                conditions={"version": current_product.version},
                current_stock=current_product.current_stock + quantity,
                version=current_product.version + 1
            )
            
            if success:
                break
            
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="재고 복구 중 충돌이 발생했습니다. 다시 시도해주세요."
                )
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"재고 복구 중 오류가 발생했습니다 Error : {e}"
                )
    
    return OrderCancelResponse(
        payment_id=payment_id,
        refunded_amount=order.price
    )


@router.get("/{payment_id}/qr", response_model=SellerPickupQRResponse,
    responses=create_error_responses({
        400:"픽업 준비가 되지 않은 주문",
        401:["인증 정보가 없음", "토큰 만료"],
        404:"주문을 찾을 수 없음"
    })            
)
async def get_order_qr(
    payment_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    픽업 QR 코드 생성, 5분 유효
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    # 주문 조회
    order = await order_repo.get_order_with_product_relation(payment_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 주문 상태 확인
    if order.status != OrderStatus.accept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="주문이 수락되지 않았습니다"
        )
    
    # JWT 기반 QR 코드 생성
    qr_data, created_at = encode_qr_data(
        user_id=order.user_id,
        payment_id=payment_id,
        product_id=order.product_id
    )
    
    return SellerPickupQRResponse(
        payment_id=payment_id,
        qr_data=qr_data,
        created_at=created_at
    )