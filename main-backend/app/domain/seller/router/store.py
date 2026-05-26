from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.domain.seller.service.store_utils import convert_store_to_response
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_store_close import SellerStoreCloseService
from app.domain.seller.schema.store import StoreCloseStateResponse, StoreDetailResponse
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store", tags=["Seller-Store"])


@router.get(
    "",
    response_model=StoreDetailResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def get_store_detail(
    store_id: CurrentSellerStoreIdDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
):
    """가게 + 주소 + SNS + 운영시간 + 이미지 + 상품 통합 조회."""
    store = await store_read_service.get_with_full_info(store_id)

    if store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="가게를 찾을 수 없습니다.",
        )

    decorated = convert_store_to_response(store, is_favorite=False)
    # seller 응답에는 is_favorite 필드를 노출하지 않는다.
    return StoreDetailResponse(**decorated.model_dump(exclude={"is_favorite"}))


@router.patch(
    "/close",
    response_model=StoreCloseStateResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        500: "가게 마감 처리 중 오류 발생",
    }),
)
@inject
async def close_store(
    store_id: CurrentSellerStoreIdDep,
    close_service: SellerStoreCloseService = Depends(
        Provide["seller_store_close_service"],
    ),
):
    """가게 마감 — reservation/accept 주문 일괄 환불 + 재고 복구."""
    refunded, message = await close_service.close(store_id)

    return StoreCloseStateResponse(
        success=True, message=message, refunded_orders=refunded,
    )
