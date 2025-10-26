from fastapi import APIRouter, HTTPException, status
from loguru import logger

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep, 
    StoreOperationInfoRepositoryDep,
    OrderCurrentItemRepositoryDep,
    StorePaymentInfoRepositoryDep,
    StoreProductInfoRepositoryDep
)
from repositories.store_product_info import StockUpdateResult
from schemas.store import StoreDetailResponse, StoreSNSInfo, StoreCloseStateResponse
from schemas.product import ProductResponse
from schemas.image import ImageUploadResponse
from schemas.store_operation import StoreOperationResponse
from schemas.store_settings import StoreAddressResponse
from schemas.order import OrderStatus
from services.payment import PaymentService
from core.object_storage import object_storage
from config.settings import settings

router = APIRouter(prefix="/store", tags=["Seller-Store"])

@router.get("", response_model=StoreDetailResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_detail(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    가게 상세 정보 조회
    
    가게의 모든 정보를 한 번에 조회합니다.
    - 기본 정보
    - 주소 정보
    - SNS 정보
    - 운영 시간
    - 이미지
    - 상품 목록
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)

    store = await store_repo.get_with_full_info(store_id)

    try:
        
        # 기본 정보
        store_detail = {
            "store_id": store.store_id,
            "store_name": store.store_name,
            "store_introduction": store.store_introduction,
            "store_phone": store.store_phone,
            "seller_email": store.seller_email,
            "created_at": store.created_at
        }
        
        # 주소 정보
        store_detail["address"] = StoreAddressResponse(
            store_id=store.store_id,
            postal_code=store.store_postal_code,
            address=store.store_address,
            detail_address=store.store_detail_address,
            sido=store.address.sido,
            sigungu=store.address.sigungu,
            bname=store.address.bname,
            lat=store.address.lat,
            lng=store.address.lng,
            nearest_station=store.address.nearest_station,
            walking_time=store.address.walking_time
        )

        
        # SNS 정보
        store_detail["sns"] = StoreSNSInfo(
            instagram=store.sns_info.instagram,
            facebook=store.sns_info.facebook,
            x=store.sns_info.x,
            homepage=store.sns_info.homepage
        )
        
        # 운영 시간 정보 변환
        store_detail["operation_times"] = [
            StoreOperationResponse.model_validate(op) for op in store.operation_info
        ]

        
        # 이미지 정보 변환
        image_responses = []
        for img in store.images:
            image_url = object_storage.get_file_url(img.image_id)
            image_responses.append(
                ImageUploadResponse(
                    image_id=img.image_id,
                    image_url=image_url,
                    is_main=img.is_main,
                    display_order=img.display_order
                )
            )
        store_detail["images"] = image_responses
        
        # 상품 정보 변환
        product_responses = []
        for product in store.products:
            nutrition_types = [info.nutrition_type for info in product.nutrition_info] if product.nutrition_info else []
            
            product_responses.append(
                ProductResponse(
                    product_id=product.product_id,
                    store_id=product.store_id,
                    product_name=product.product_name,
                    description=product.description,
                    initial_stock=product.initial_stock,
                    current_stock=product.current_stock,
                    price=product.price,
                    sale=product.sale,
                    version=product.version,
                    nutrition_types=nutrition_types
                )
            )
        store_detail["products"] = product_responses
        
        return StoreDetailResponse(**store_detail)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"가게 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/close", response_model=StoreCloseStateResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        500: "가게 마감 처리 중 오류 발생"
    })
)
async def close_store(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    payment_info_repo: StorePaymentInfoRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
):
    """
    가게 마감 처리
    
    - 가게의 운영 상태를 마감으로 변경
    - reservation/accept 상태의 모든 주문을 환불 처리
    """
    seller_email = current_user["sub"]
    
    try:
        store_id = await get_store_id_by_email(seller_email, store_repo)
        
        # 오늘 날짜의 가게 운영 정보만 업데이트
        today_operation = await operation_repo.get_today_operation_info(store_id)
        
        if today_operation:
            await operation_repo.update_open_status(
                operation_id=today_operation.operation_id,
                is_currently_open=False
            )

        payment_info = await payment_info_repo.get_by_store_id(store_id)
        if not payment_info or not payment_info.portone_secret_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="가게의 결제 설정이 완료되지 않았습니다"
            )
        
        current_orders = await order_repo.get_store_current_orders_with_relations(store_id)
        
        refund_count = 0
        
        for order in current_orders:
            if order.status in [OrderStatus.reservation, OrderStatus.accept]:
                try:
                    refund_result = await PaymentService.process_refund(
                        payment_id=order.payment_id,
                        secret_key=payment_info.portone_secret_key,
                        reason="‘기타 사정’ 으로 주문이 취소되었어요."
                    )
                    
                    if refund_result.get("success"):
                        # 주문 취소 처리
                        quantity = await order_repo.cancel_order(
                            payment_id=order.payment_id,
                            cancel_reason="‘기타 사정’ 으로 주문이 취소되었어요."
                        )
                        
                        # 재고 복구
                        max_retries = settings.MAX_RETRY_LOCK
                        for attempt in range(max_retries):
                            result = await product_repo.adjust_purchased_stock(order.product_id, -quantity)
                            
                            if result == StockUpdateResult.SUCCESS:
                                break
                            
                            if attempt == max_retries - 1:
                                logger.error(f"가게 마감 처리로 인한 환불 중 - 재고 복구 오류 발생: {str(e)}")
                                break
                        
                        refund_count += 1
                    else:
                        logger.error(f"가게 마감 처리로 인한 환불 중 - 환불 오류 발생: {str(e)}")
                        
                except Exception as e:
                    logger.error(f"가게 마감 처리로 인한 환불 중 - 오류 발생: {str(e)}")
        
        # 결과 반환
        return {
            "success": True,
            "message": "가게가 마감되었습니다",
            "refunded_orders": refund_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"가게 마감 처리 중 오류가 발생했습니다: {str(e)}"
        )