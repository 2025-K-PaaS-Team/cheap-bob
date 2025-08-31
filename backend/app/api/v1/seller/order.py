from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime

from api.deps import CurrentSellerDep, AsyncSessionDep
from repositories.store import StoreRepository
from repositories.order_current_item import OrderCurrentItemRepository
from database.models.order_current_item import OrderCurrentItem, OrderStatus
from database.models.store_product_info import StoreProductInfo
from schemas.order import (
    OrderItemResponse,
    OrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse
)
from services.payment import PaymentService

from repositories.store_product_info import StoreProductInfoRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from config.settings import settings

router = APIRouter(prefix="/orders", tags=["Seller-Order"])


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_order_repository(session: AsyncSessionDep) -> OrderCurrentItemRepository:
    return OrderCurrentItemRepository(session)


def get_product_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


def get_payment_info_repository(session: AsyncSessionDep) -> StorePaymentInfoRepository:
    return StorePaymentInfoRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
OrderRepositoryDep = Annotated[OrderCurrentItemRepository, Depends(get_order_repository)]
ProductRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_product_repository)]
PaymentInfoRepositoryDep = Annotated[StorePaymentInfoRepository, Depends(get_payment_info_repository)]


@router.get("/{store_id}", response_model=OrderListResponse)
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
        .order_by(OrderCurrentItem.created_at.desc())
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
            created_at=order.created_at,
            confirmed_at=order.confirmed_at
        )
        order_responses.append(order_response)
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.get("/{store_id}/pending", response_model=OrderListResponse)
async def get_pending_orders(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    session: AsyncSessionDep
):
    """
    처리 대기중인 주문 조회
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
                OrderCurrentItem.status == OrderStatus.reservation
            )
        )
        .options(selectinload(OrderCurrentItem.product))
        .order_by(OrderCurrentItem.created_at)
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
            created_at=order.created_at,
            confirmed_at=order.confirmed_at
        )
        order_responses.append(order_response)
    
    return OrderListResponse(
        orders=order_responses,
        total=len(order_responses)
    )


@router.patch("/{order_id}/accept", response_model=OrderItemResponse)
async def update_order_accept(
    order_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderRepositoryDep,
    session: AsyncSessionDep
):
    """
    주문 수락
    """
    
    stmt = (
        select(OrderCurrentItem)
        .where(OrderCurrentItem.payment_id == order_id)
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
        order_id,
        status=OrderStatus.complete,
        confirmed_at=datetime.now()
    )
    
    # response 포맷으로 변환
    return OrderItemResponse(
        payment_id=updated_order.payment_id,
        product_id=updated_order.product_id,
        product_name=order.product.product_name,
        quantity=updated_order.quantity,
        price=updated_order.price,
        status=updated_order.status,
        created_at=updated_order.created_at,
        confirmed_at=updated_order.confirmed_at
    )


@router.post("/{order_id}/cancel", response_model=OrderCancelResponse)
async def cancel_order(
    order_id: str,
    request: OrderCancelRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    order_repo: OrderRepositoryDep,
    product_repo: ProductRepositoryDep,
    payment_info_repo: PaymentInfoRepositoryDep,
    session: AsyncSessionDep
):
    """
    주문 취소 (포트원 환불 포함)
    """
    
    stmt = (
        select(OrderCurrentItem)
        .where(OrderCurrentItem.payment_id == order_id)
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
        payment_id=order_id,
        secret_key=payment_info.portone_secret_key,
        reason=request.reason
    )
    
    if not refund_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=refund_result.get("error", "환불 처리 중 오류가 발생했습니다")
        )
    
    quantity = await order_repo.cancel_order(order_id)
    
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
                    detail="재고 복구 중 오류가 발생했습니다"
                )
    
    return OrderCancelResponse(
        payment_id=order_id,
        status="cancelled",
        message="주문이 성공적으로 취소되었습니다",
        refunded_amount=order.price
    )