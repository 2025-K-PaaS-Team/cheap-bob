from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from loguru import logger

from utils.docs_error import create_error_responses

from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    StoreProductInfoRepositoryDep,
    CartItemRepositoryDep,
    OrderCurrentItemRepositoryDep,
    StorePaymentInfoRepositoryDep
)
from repositories.store_product_info import StockUpdateResult
from schemas.order import OrderStatus
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


async def restore_product_stock(
    product_id: str,
    quantity: int,
    product_repo: StoreProductInfoRepositoryDep
) -> bool:
    """
    낙관적 락을 사용하여 상품 구매 수량을 복구 (구매 취소)
    
    Args:
        product_id: 상품 ID
        quantity: 복구할 수량
        product_repo: 상품 레포지토리
        
    Returns:
        성공 여부
        
    Raises:
        HTTPException: 재고 복구 실패 시
    """
    
    max_retries = settings.MAX_RETRY_LOCK
    
    for attempt in range(max_retries):
        result = await product_repo.adjust_purchased_stock(product_id, -quantity)
        
        if result == StockUpdateResult.SUCCESS:
            return True
        
        if attempt == max_retries - 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="재고 복구 중 충돌이 발생했습니다. 다시 시도해주세요."
            )
    
    return False




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
    product_repo: StoreProductInfoRepositoryDep,
    cart_repo: CartItemRepositoryDep,
    payment_info_repo: StorePaymentInfoRepositoryDep
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
    
    # 결제 ID 생성
    payment_id = generate_payment_id()
    
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        result = await product_repo.adjust_purchased_stock(request.product_id, request.quantity)
        
        if result == StockUpdateResult.SUCCESS:
            break
        elif result == StockUpdateResult.INSUFFICIENT_STOCK:
            current_product = await product_repo.get_by_product_id(request.product_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"재고가 부족합니다. 현재 재고: {current_product.current_stock}개"
            )
        
        if attempt == max_retries - 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="재고 차감 중 충돌이 발생했습니다. 다시 시도해주세요."
            )
    
    if product.sale:
        discounted = product.price * (100 - product.sale) / 100
        round_price = ((discounted + 99) // 100) * 100
        total_amount = round_price * request.quantity
        
    else:
        total_amount = product.price * request.quantity 
    
    # 장바구니에 등록
    cart_data = {
        "payment_id": payment_id,
        "product_id": request.product_id,
        "user_id": current_user["sub"],
        "quantity": request.quantity,
        "price": product.price,
        "sale": product.sale,
        "total_amount": total_amount
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
        quantity=request.quantity,
        price=product.price,
        sale=product.sale,
        total_amount=total_amount
    )


@router.post("/confirm", response_model=PaymentResponse,
    responses=create_error_responses({
        400: "결제 검증에 실패",
        401:["인증 정보가 없음", "토큰 만료"],
        403: "결제 권한이 없음",
        404:["결제 정보를 찾을 수 없음", "상품 정보를 찾을 수 없음"],
        409: "재고 복구 중, 동시성 충돌 발생"
    })  
)
async def confirm_payment(
    request: PaymentConfirmRequest,
    current_user: CurrentCustomerDep,
    cart_repo: CartItemRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    payment_info_repo: StorePaymentInfoRepositoryDep
):
    """
    결제 최종 확인 API - 포트원에서 결제가 성공했는지 확인
    """
    cart_item = None
    product = None
    payment_info = None
    
    try:
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
        
        if not payment_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="가게의 결제 설정이 완료되지 않았습니다"
            )
        
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
            "sale": cart_item.sale,
            "total_amount" : cart_item.total_amount,
            "status": OrderStatus.reservation,
            "reservation_at": datetime.now(timezone.utc)
        }
        
        await order_repo.create(**order_data)
        
        # 장바구니에서 삭제
        await cart_repo.delete(cart_item.payment_id)
        
        return PaymentResponse(
            payment_id=request.payment_id
        )
        
    except Exception as e:
        # 에러 발생 시 환불 및 재고 복구 처리
        logger.error(f"결제 확인 중 오류 발생: {str(e)}")
        
        # 환불 처리가 필요한 경우 (결제 정보와 상품 정보가 있는 경우)
        if cart_item and product and payment_info:
            try:
                # 포트원 환불 처리
                refund_result = await PaymentService.process_refund(
                    payment_id=request.payment_id,
                    secret_key=payment_info.portone_secret_key,
                    reason=f"결제 확인 중 오류 발생: {str(e)}"
                )
                
                logger.info(f"환불 처리 완료: {refund_result}")
                
                # 재고 복구
                await restore_product_stock(
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    product_repo=product_repo
                )
                
                logger.info(f"재고 복구 완료: 상품 ID {cart_item.product_id}, 수량 {cart_item.quantity}")
                
                # 장바구니에서 삭제
                await cart_repo.delete(cart_item.payment_id)
                
            except Exception as refund_error:
                logger.error(f"환불/재고복구 처리 중 오류: {str(refund_error)}")
        
        # 원본 에러를 다시 발생시킴
        raise