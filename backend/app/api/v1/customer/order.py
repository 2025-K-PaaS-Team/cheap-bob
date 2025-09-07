from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime

from utils.docs_error import create_error_responses

from api.deps import CurrentCustomerDep, AsyncSessionDep
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.store_product_info import StoreProductInfoRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from database.models.order_current_item import OrderCurrentItem
from database.models.store_product_info import StoreProductInfo
from schemas.customer_order import (
    CustomerOrderItemResponse,
    CustomerOrderListResponse,
    CustomerOrderDetailResponse,
    CustomerOrderCancelRequest,
    CustomerOrderCancelResponse,
    PickupCompleteRequest
)
from schemas.order import OrderStatus
from services.payment import PaymentService
from config.settings import settings
from utils.qr_generator import validate_qr_data

router = APIRouter(prefix="/orders", tags=["Customer-Order"])


def get_order_repository(session: AsyncSessionDep) -> OrderCurrentItemRepository:
    return OrderCurrentItemRepository(session)


def get_product_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


def get_payment_info_repository(session: AsyncSessionDep) -> StorePaymentInfoRepository:
    return StorePaymentInfoRepository(session)


OrderRepositoryDep = Annotated[OrderCurrentItemRepository, Depends(get_order_repository)]
ProductRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_product_repository)]
PaymentInfoRepositoryDep = Annotated[StorePaymentInfoRepository, Depends(get_payment_info_repository)]


@router.get("", response_model=CustomerOrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_order_history(
    current_user: CurrentCustomerDep,
    session: AsyncSessionDep
):
    """
    주문 내역 조회 - 모든 주문 조회
    """
    
    # 사용자의 모든 주문 조회
    stmt = (
        select(OrderCurrentItem)
        .where(OrderCurrentItem.user_id == current_user["sub"])
        .options(
            selectinload(OrderCurrentItem.product).selectinload(StoreProductInfo.store)
        )
        .order_by(OrderCurrentItem.reservation_at.desc())
    )
    
    result = await session.execute(stmt)
    orders = result.scalars().all()
    
    # response 포맷으로 변환
    order_responses = []
    for order in orders:
        order_response = CustomerOrderItemResponse(
            payment_id=order.payment_id,
            product_id=order.product_id,
            product_name=order.product.product_name,
            store_id=order.product.store_id,
            store_name=order.product.store.store_name,
            quantity=order.quantity,
            price=order.price,
            status=order.status,
            reservation_at=order.reservation_at,
            accepted_at=order.accepted_at,
            pickup_ready_at=order.pickup_ready_at,
            completed_at=order.completed_at,
            canceled_at=order.canceled_at
        )
        order_responses.append(order_response)
    
    return CustomerOrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/current", response_model=CustomerOrderListResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_current_orders(
    current_user: CurrentCustomerDep,
    session: AsyncSessionDep
):
    """
    현재 진행중인 주문 조회 (reservation, accepted, pickup)
    """
    
    # 사용자의 현재 진행중인 주문만 조회 (reservation, accepted, pickup)
    stmt = (
        select(OrderCurrentItem)
        .where(OrderCurrentItem.user_id == current_user["sub"])
        .where(OrderCurrentItem.status.in_([OrderStatus.reservation, OrderStatus.accept, OrderStatus.pickup]))
        .options(
            selectinload(OrderCurrentItem.product).selectinload(StoreProductInfo.store)
        )
        .order_by(OrderCurrentItem.reservation_at.desc())
    )
    
    result = await session.execute(stmt)
    orders = result.scalars().all()
    
    # response 포맷으로 변환
    order_responses = []
    for order in orders:
        order_response = CustomerOrderItemResponse(
            payment_id=order.payment_id,
            product_id=order.product_id,
            product_name=order.product.product_name,
            store_id=order.product.store_id,
            store_name=order.product.store.store_name,
            quantity=order.quantity,
            price=order.price,
            status=order.status,
            reservation_at=order.reservation_at,
            accepted_at=order.accepted_at,
            pickup_ready_at=order.pickup_ready_at,
            completed_at=order.completed_at,
            canceled_at=order.canceled_at
        )
        order_responses.append(order_response)
    
    return CustomerOrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/{payment_id}", response_model=CustomerOrderDetailResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403:"주문을 확인할 권한이 없음",
        404: "주문을 찾을 수 없음"
    })            
)
async def get_order_detail(
    payment_id: str,
    current_user: CurrentCustomerDep,
    session: AsyncSessionDep
):
    """
    주문 상세 정보 조회
    """
    
    # 주문 조회 (with product info)
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
    
    # 사용자 검증
    if order.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 주문을 조회할 권한이 없습니다"
        )
    
    # 단가와 할인율 계산
    unit_price = order.product.price
    discount_rate = order.product.sale
    
    return CustomerOrderDetailResponse(
        payment_id=order.payment_id,
        product_id=order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=order.quantity,
        price=order.price,
        unit_price=unit_price,
        discount_rate=discount_rate,
        status=order.status,
        reservation_at=order.reservation_at,
        accepted_at=order.accepted_at,
        pickup_ready_at=order.pickup_ready_at,
        completed_at=order.completed_at
    )
    
@router.delete("/{payment_id}", response_model=CustomerOrderCancelResponse,
    responses=create_error_responses({
        400: ["이미 취소된 주문", "이미 승인된 주문"],
        401:["인증 정보가 없음", "토큰 만료"],
        403:"주문을 확인할 권한이 없음",
        404:"상품을 찾을 수 없음",
        409: "동시성 충돌 발생"
    })               
)
async def delete_order(
    payment_id: str,
    request: CustomerOrderCancelRequest,
    current_user: CurrentCustomerDep,
    order_repo: OrderRepositoryDep,
    product_repo: ProductRepositoryDep,
    payment_info_repo: PaymentInfoRepositoryDep,
    session: AsyncSessionDep
):
    """
    주문 취소 (포트원 환불 포함)
    """
    
    # 주문 조회 (with product info)
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
    
    # 사용자 검증
    if order.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 주문을 취소할 권한이 없습니다"
        )
    
    # 이미 취소된 주문인지 확인
    if order.status == OrderStatus.cancel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 취소된 주문입니다"
        )
    
    # 수락된 주문은 취소 불가
    if order.status in [OrderStatus.accept, OrderStatus.pickup, OrderStatus.complete]:
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
    quantity = await order_repo.cancel_order(payment_id)
    
    # 낙관적 락을 사용하여 재고 복구
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        try:
            # 최신 상품 정보 조회
            current_product = await product_repo.get_by_product_id(order.product_id)
            
            # 낙관적 락을 사용한 재고 업데이트
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
                
        except HTTPException:
            raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="재고 복구 중 오류가 발생했습니다"
                )
    
    return CustomerOrderCancelResponse(
        payment_id=payment_id,
        refunded_amount=order.price
    )


@router.patch("/{payment_id}/pickup-complete", response_model=CustomerOrderItemResponse,
    responses=create_error_responses({
        400:["유효하지 않은 QR 코드", "권한이 없는 사용자", "이미 픽업 완료"],
        401:["인증 정보가 없음", "토큰 만료"],
        404:["주문을 찾을 수 없음", "QR 코드를 찾을 수 없음"]
    })               
)
async def complete_pickup(
    payment_id: str,
    request: PickupCompleteRequest,
    current_user: CurrentCustomerDep,
    order_repo: OrderRepositoryDep,
    session: AsyncSessionDep
):
    """
    픽업 완료 처리 (QR 코드 검증)
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
    
    # 주문 상태 확인
    if order.status != OrderStatus.pickup:
        if order.status == OrderStatus.complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 픽업이 완료된 주문입니다"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="픽업 준비가 되지 않은 주문입니다"
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
    
    return CustomerOrderItemResponse(
        payment_id=completed_order.payment_id,
        product_id=completed_order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=completed_order.quantity,
        price=completed_order.price,
        status=completed_order.status,
        reservation_at=completed_order.reservation_at,
        accepted_at=completed_order.accepted_at,
        pickup_ready_at=completed_order.pickup_ready_at,
        completed_at=completed_order.completed_at,
        canceled_at=order.canceled_at
    )