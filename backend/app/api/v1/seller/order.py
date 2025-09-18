from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from utils.docs_error import create_error_responses

from api.deps.auth import CurrentSellerDep
from api.deps.database import AsyncSessionDep
from api.deps.repository import (
    StoreRepositoryDep,
    OrderCurrentItemRepositoryDep,
    StoreProductInfoRepositoryDep,
    StorePaymentInfoRepositoryDep
)
from database.models.order_current_item import OrderCurrentItem
from database.models.store_product_info import StoreProductInfo
from schemas.seller_order import (
    OrderItemResponse,
    OrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse,
    OrderStatus,
    PickupQRResponse
)
from services.payment import PaymentService
from utils.qr_generator import encode_qr_data
from config.settings import settings

router = APIRouter(prefix="/orders", tags=["Seller-Order"])


@router.get("/{store_id}", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })          
)
async def get_store_orders(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    session: AsyncSessionDep
):
    """
    가게의 주문 목록 조회
    """
    
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 가게를 조회할 권한이 없습니다"
        )
    
    stmt = (
        select(OrderCurrentItem)
        .join(StoreProductInfo, OrderCurrentItem.product_id == StoreProductInfo.product_id)
        .where(StoreProductInfo.store_id == store_id)
        .options(selectinload(OrderCurrentItem.product))
        .order_by(OrderCurrentItem.reservation_at.desc())
    )
    
    result = await session.execute(stmt)
    orders = result.scalars().all()
    
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
            canceled_at=order.canceled_at
        )
        order_responses.append(order_response)
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/{store_id}/pending", response_model=OrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })                 
)
async def get_pending_orders(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    session: AsyncSessionDep
):
    """
    처리 대기중인 주문 조회 (reservation, accepted, pickup, complete)
    """
    
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 가게가 없습니다"
        )
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 가게를 조회할 권한이 없습니다"
        )
    
    stmt = (
        select(OrderCurrentItem)
        .join(StoreProductInfo, OrderCurrentItem.product_id == StoreProductInfo.product_id)
        .where(
            and_(
                StoreProductInfo.store_id == store_id,
                OrderCurrentItem.status.in_([OrderStatus.reservation, OrderStatus.accept])
            )
        )
        .options(selectinload(OrderCurrentItem.product))
        .order_by(OrderCurrentItem.reservation_at)
    )
    
    result = await session.execute(stmt)
    orders = result.scalars().all()
    
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
            canceled_at=order.canceled_at
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
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })                   
)
async def update_order_accept(
    payment_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    session: AsyncSessionDep
):
    """
    주문 수락
    """
    
    stmt = (
        select(OrderCurrentItem)
        .where(OrderCurrentItem.payment_id == payment_id)
        .options(selectinload(OrderCurrentItem.product))
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    store = await store_repo.get_by_store_id(order.product.store_id)
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 주문을 처리할 권한이 없습니다"
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
        canceled_at=order.canceled_at
    )


@router.post("/{payment_id}/cancel", response_model=OrderCancelResponse,
    responses=create_error_responses({
        400:"이미 취소한 주문",
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
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
    payment_info_repo: StorePaymentInfoRepositoryDep,
    session: AsyncSessionDep
):
    """
    주문 취소 (포트원 환불 포함)
    """
    
    stmt = (
        select(OrderCurrentItem)
        .where(OrderCurrentItem.payment_id == payment_id)
        .options(selectinload(OrderCurrentItem.product))
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    store = await store_repo.get_by_store_id(order.product.store_id)
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 주문을 취소할 권한이 없습니다"
        )
    
    if order.status == OrderStatus.cancel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 취소된 주문입니다"
        )
    
    # 가게의 결제 정보 조회
    payment_info = await payment_info_repo.get_by_store_id(store.store_id)
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
    
    quantity = await order_repo.cancel_order(payment_id)
    
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
        status="cancelled",
        message="주문이 성공적으로 취소되었습니다",
        refunded_amount=order.price
    )


@router.get("/{payment_id}/qr", response_model=PickupQRResponse,
    responses=create_error_responses({
        400:"픽업 준비가 되지 않은 주문",
        401:["인증 정보가 없음", "토큰 만료"],
        403:"가게를 수정할 수 있는 권한이 없음",
        404:"주문을 찾을 수 없음"
    })            
)
async def get_order_qr(
    payment_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    session: AsyncSessionDep
):
    """
    픽업 QR 코드 생성, 5분 유효
    """
    
    # 주문 조회
    stmt = (
        select(OrderCurrentItem)
        .where(OrderCurrentItem.payment_id == payment_id)
        .options(selectinload(OrderCurrentItem.product))
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문을 찾을 수 없습니다"
        )
    
    # 가게 권한 확인
    store = await store_repo.get_by_store_id(order.product.store_id)
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 주문의 QR 코드를 조회할 권한이 없습니다"
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
    
    return PickupQRResponse(
        payment_id=payment_id,
        qr_data=qr_data,
        created_at=created_at
    )