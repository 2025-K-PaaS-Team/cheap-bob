from typing import Dict, Annotated
from fastapi import APIRouter, HTTPException, Path, Depends, status
from datetime import datetime
from loguru import logger

from utils.docs_error import create_error_responses

from api.deps import CurrentCustomerDep, AsyncSessionDep
from repositories.store_product_info import StoreProductInfoRepository
from repositories.cart_item import CartItemRepository
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from database.models.order_current_item import OrderStatus
from schemas.payment import (
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentConfirmRequest,
    PaymentResponse
)
from services.payment import PaymentService
from utils.id_generator import generate_payment_id
from config.settings import settings

router = APIRouter(prefix="/payment", tags=["Customer-Payment"])


def get_product_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


def get_cart_repository(session: AsyncSessionDep) -> CartItemRepository:
    return CartItemRepository(session)


def get_order_repository(session: AsyncSessionDep) -> OrderCurrentItemRepository:
    return OrderCurrentItemRepository(session)


def get_payment_info_repository(session: AsyncSessionDep) -> StorePaymentInfoRepository:
    return StorePaymentInfoRepository(session)


ProductRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_product_repository)]
CartRepositoryDep = Annotated[CartItemRepository, Depends(get_cart_repository)]
OrderRepositoryDep = Annotated[OrderCurrentItemRepository, Depends(get_order_repository)]
PaymentInfoRepositoryDep = Annotated[StorePaymentInfoRepository, Depends(get_payment_info_repository)]


@router.post("/init", response_model=PaymentInitResponse,
    responses=create_error_responses({
        400: "재고가 없음",
        401:["인증 정보가 없음", "토큰 만료"],
        404:"상품을 찾을 수 없음",
        409: "동시성 충돌 발생"
    })
)
async def init_payment(
    request: PaymentInitRequest,
    current_user: CurrentCustomerDep,
    product_repo: ProductRepositoryDep,
    cart_repo: CartRepositoryDep,
    payment_info_repo: PaymentInfoRepositoryDep
):
    """
    결제 초기화 API - 상품과 수량을 확인하고 결제 세션을 생성
    """
    # 상품 조회
    product = await product_repo.get_by_product_id(request.product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 재고 확인
    if product.current_stock < request.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"재고가 부족합니다. 현재 재고: {product.current_stock}개"
        )
    
    # 총 금액 계산
    total_amount = product.price * request.quantity
    if product.sale:
        total_amount = int(total_amount * (100 - product.sale) / 100)
    
    # 결제 ID 생성
    payment_id = generate_payment_id()
    
    # 낙관적 락을 사용하여 재고 차감
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        try:
            # 최신 상품 정보 조회
            current_product = await product_repo.get_by_product_id(request.product_id)
            
            # 재고 확인
            if current_product.current_stock < request.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"재고가 부족합니다. 현재 재고: {current_product.current_stock}개"
                )
            
            # 낙관적 락을 사용한 재고 차감
            success = await product_repo.update_lock(
                request.product_id,
                conditions={"version": current_product.version},
                current_stock=current_product.current_stock - request.quantity,
                version=current_product.version + 1
            )
            
            if success:
                break
            
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="재고 차감 중 충돌이 발생했습니다. 다시 시도해주세요."
                )
                
        except HTTPException:
            raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="재고 차감 중 오류가 발생했습니다"
                )
    
    # 장바구니에 등록
    cart_data = {
        "payment_id": payment_id,
        "product_id": request.product_id,
        "user_id": current_user["sub"],
        "quantity": request.quantity,
        "price": total_amount
    }
    
    await cart_repo.create(**cart_data)
    
    # 포트원 설정 정보 가져오기
    payment_info = await payment_info_repo.get_by_store_id(product.store_id)
    
    if not payment_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="가게의 결제 설정이 완료되지 않았습니다"
        )
    
    if not payment_info.portone_channel_id or not payment_info.portone_store_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="포트원 설정이 완료되지 않았습니다"
        )
    
    return PaymentInitResponse(
        payment_id=payment_id,
        channel_id=payment_info.portone_channel_id,
        store_id=payment_info.portone_store_id,
        total_amount=total_amount
    )


@router.post("/confirm", response_model=PaymentResponse,
    responses=create_error_responses({
        400: "결제 검증에 실패",
        401:["인증 정보가 없음", "토큰 만료"],
        403: "결제 권한이 없음",
        404:["결제 정보를 찾을 수 없음", "상품 정보를 찾을 수 없음"]
    })  
)
async def confirm_payment(
    request: PaymentConfirmRequest,
    current_user: CurrentCustomerDep,
    cart_repo: CartRepositoryDep,
    order_repo: OrderRepositoryDep,
    product_repo: ProductRepositoryDep,
    payment_info_repo: PaymentInfoRepositoryDep
):
    """
    결제 최종 확인 API - 포트원에서 결제가 성공했는지 확인
    """
    # 장바구니에서 결제 정보 조회
    cart_item = await cart_repo.get_by_payment_id(request.payment_id)
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="결제 정보를 찾을 수 없습니다"
        )
    
    # 사용자 검증
    if cart_item.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="결제에 대한 권한이 없습니다"
        )
    
    # 상품 정보 조회하여 store_id 획득
    product = await product_repo.get_by_product_id(cart_item.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품 정보를 찾을 수 없습니다"
        )
    
    # 가게의 결제 정보 조회
    payment_info = await payment_info_repo.get_by_store_id(product.store_id)
    
    # PaymentService를 통해 결제 검증
    result = await PaymentService.verify_payment(
        request.payment_id,
        secret_key=payment_info.portone_secret_key
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="결제 검증에 실패했습니다"
        )
    
    logger.info("유저 ID({}) / 결제({}) / 상품({}) / 금액({})".format(
        cart_item.user_id,
        result["payment_info"]['payment_method'],
        result["payment_info"]['good_name'],
        result["payment_info"]['amount']
    ))
    
    # 주문 생성
    order_data = {
        "payment_id": cart_item.payment_id,
        "product_id": cart_item.product_id,
        "user_id": cart_item.user_id,
        "quantity": cart_item.quantity,
        "price": cart_item.price,
        "status": OrderStatus.reservation,
        "created_at": datetime.now()
    }
    
    await order_repo.create(**order_data)
    
    # 장바구니에서 삭제
    await cart_repo.delete(cart_item.payment_id)
    
    return PaymentResponse(
        payment_id=request.payment_id
    )


@router.delete("/cancel/{payment_id}", response_model=PaymentResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "결제 취소 권한이 없음",
        404:["결제 정보를 찾을 수 없음", "장바구니 항목을 찾을 수 없음"],
        409: "재고 복구 중, 동시성 충돌 발생"
    })               
)
async def cancel_payment(
    payment_id: str,
    current_user: CurrentCustomerDep,
    cart_repo: CartRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    결제 취소 API - 사용자가 결제 중 취소 시 장바구니 삭제 및 재고 복구
    """
    # 장바구니에서 결제 정보 조회
    cart_item = await cart_repo.get_by_payment_id(payment_id)
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="결제 정보를 찾을 수 없습니다"
        )
    
    # 사용자 검증
    if cart_item.user_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 결제를 취소할 권한이 없습니다"
        )
    
    # 장바구니에서 삭제 및 수량 반환
    quantity = await cart_repo.delete_paymen_id_and_return_quantity(payment_id)
    
    if quantity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장바구니 항목을 찾을 수 없습니다"
        )
    
    # 낙관적 락을 사용하여 재고 복구
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        try:
            # 최신 상품 정보 조회
            current_product = await product_repo.get_by_product_id(cart_item.product_id)
            
            # 낙관적 락을 사용한 재고 복구
            success = await product_repo.update_lock(
                cart_item.product_id,
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
    
    return PaymentResponse(
        payment_id=payment_id
    )