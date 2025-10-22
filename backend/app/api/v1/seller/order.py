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
    OrderHistoryItemRepositoryDep,
    StoreProductInfoRepositoryDep,
    StorePaymentInfoRepositoryDep
)
from repositories.store_product_info import StockUpdateResult
from schemas.order import (
    OrderItemResponse,
    OrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse,
    OrderStatus,
    SellerPickupQRResponse,
    DashboardResponse,
    DashboardStockItem
)
from services.payment import PaymentService
from services.email import email_service
from config.settings import settings

router = APIRouter(prefix="/store/orders", tags=["Seller-Order"])


@router.get("", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })          
)
async def get_store_orders(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    history_repo: OrderHistoryItemRepositoryDep
):
    """
    가게의 주문 목록 조회 (당일 + 과거)
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    # 당일 주문 조회
    current_orders = await order_repo.get_store_orders_with_relations(store_id)
    
    # 과거 주문 조회
    history_orders = await history_repo.get_store_history(store_id)
    
    order_responses = []
    
    # 당일 주문 처리
    for order in current_orders:
        order_response = OrderItemResponse(
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
        order_responses.append(order_response)
    
    # 과거 주문 처리
    for history_order in history_orders:
        
        order_response = OrderItemResponse(
            payment_id=history_order.payment_id,
            customer_id=history_order.customer_id,
            customer_nickname=history_order.customer_nickname,
            customer_phone_number=history_order.customer_phone_number,
            product_id=history_order.product_id,
            product_name=history_order.product_name,
            store_id=store_id,
            store_name=history_order.store_name,
            quantity=history_order.quantity,
            price=history_order.price,
            sale=history_order.sale,
            total_amount=history_order.total_amount,
            status=history_order.status,
            reservation_at=history_order.reservation_at,
            accepted_at=history_order.accepted_at,
            completed_at=history_order.completed_at,
            canceled_at=history_order.canceled_at,
            cancel_reason=history_order.cancel_reason,
            preferred_menus=parse_comma_separated_string(history_order.preferred_menus),
            nutrition_types=parse_comma_separated_string(history_order.nutrition_types),
            allergies=parse_comma_separated_string(history_order.allergies),
            topping_types=parse_comma_separated_string(history_order.topping_types)
        )
        order_responses.append(order_response)
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/today", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })                 
)
async def get_order_today(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep
):
    """
    당일 주문 조회
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    orders = await order_repo.get_store_current_orders_with_relations(store_id)
    
    order_responses = []
    for order in orders:
        order_response = OrderItemResponse(
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
    
    # 주문 확정 이메일 서비스
    if email_service.is_configured():
        store = await store_repo.get_by_store_id(store_id)
        await email_service.send_template(
            recipient_email=order.customer_id,
            store_name=store.store_name,
            template_type="accept"
        )
    
    # response 포맷으로 변환
    return OrderItemResponse(
        payment_id=updated_order.payment_id,
        customer_id=order.customer_id,
        customer_nickname=order.customer.detail.nickname,
        customer_phone_number=order.customer.detail.phone_number,
        product_id=updated_order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=updated_order.quantity,
        price=updated_order.price,
        sale=updated_order.sale,
        total_amount=order.total_amount,
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


@router.delete("/{payment_id}/cancel", response_model=OrderCancelResponse,
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
    
    # 판매자 주문 취소 이메일 서비스
    if email_service.is_configured():
        store = await store_repo.get_by_store_id(store_id)
        await email_service.send_template(
            recipient_email=order.customer_id,
            store_name=store.store_name,
            template_type="seller_cancel"
        )
    
    return OrderCancelResponse(
        payment_id=payment_id,
        quantity=order.quantity,
        price=order.price,
        sale=order.sale,
        total_amount=order.total_amount,
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
        customer_id=order.customer_id,
        payment_id=payment_id,
        product_id=order.product_id
    )
    
    return SellerPickupQRResponse(
        payment_id=payment_id,
        qr_data=qr_data,
        created_at=created_at
    )


@router.get("/dashboard", response_model=DashboardResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })                 
)
async def get_dashboard(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
):
    """
    대시보드 - 재고 현황 조회
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    store_current_orders = await order_repo.get_by_store_id(store_id)
    
    # 가게의 모든 상품 조회
    products = await product_repo.get_by_store_id(store_id)
    
    product_order_quantities = {}
    for order in store_current_orders:
        if order.status != OrderStatus.cancel:
            if order.product_id not in product_order_quantities:
                product_order_quantities[order.product_id] = 0
            product_order_quantities[order.product_id] += order.quantity
    
    # 대시보드 응답 생성
    dashboard_items = []
    for product in products:
        purchased_stock = product_order_quantities.get(product.product_id, 0)
        
        current_stock = product.initial_stock - purchased_stock + product.admin_adjustment
        
        dashboard_item = DashboardStockItem(
            product_id=product.product_id,
            product_name=product.product_name,
            current_stock=current_stock,
            initial_stock=product.initial_stock,
            purchased_stock=purchased_stock,
            adjustment_stock=product.admin_adjustment
        )
        dashboard_items.append(dashboard_item)
    
    return DashboardResponse(
        items=dashboard_items,
        total_items=len(dashboard_items)
    )