from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.store_auth import verify_store_owner
from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep,
    AddressRepositoryDep,
    StoreSNSRepositoryDep,
    StoreOperationInfoRepositoryDep,
    StoreImageRepositoryDep,
    StoreProductInfoRepositoryDep
)
from schemas.store import StoreDetailResponse, StoreSNSInfo
from schemas.product import ProductResponse
from schemas.image import ImageUploadResponse
from schemas.store_operation import StoreOperationResponse
from schemas.store_settings import StoreAddressResponse

router = APIRouter(prefix="/store", tags=["Seller-Store"])

async def verify_store_owner(
    store_id: str,
    seller_email: str,
    store_repo: StoreRepositoryDep
) -> None:
    """
    가게 소유권 검증
    
    Args:
        store_id: 검증할 가게 ID
        seller_email: 현재 로그인한 판매자 이메일
        store_repo: 가게 레포지토리
    
    Raises:
        HTTPException: 가게를 찾을 수 없거나 권한이 없는 경우
    """
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    
    if store.seller_email != seller_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가게 정보에 접근할 권한이 없습니다."
        )
        
    return store

@router.get("/{store_id}", response_model=StoreDetailResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 조회할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_detail(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    address_repo: AddressRepositoryDep,
    sns_repo: StoreSNSRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep,
    image_repo: StoreImageRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
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
    
    store = await verify_store_owner(store_id, seller_email, store_repo)

    try:
        # 주소 정보 조회
        address = await address_repo.get(store.address_id)
        if address:
            address_data = StoreAddressResponse(
                store_id=store_id,
                postal_code=store.store_postal_code,
                address=store.store_address,
                detail_address=store.store_detail_address,
                sido=address.sido,
                sigungu=address.sigungu,
                bname=address.bname,
                lat=address.lat,
                lng=address.lng
            )
        
        # SNS 정보 조회
        sns_info = await sns_repo.get_by_store_id(store_id)
        sns_data = StoreSNSInfo(
            instagram=sns_info.instagram_url if sns_info else None,
            facebook=sns_info.facebook_url if sns_info else None,
            x=sns_info.x_url if sns_info else None,
            homepage=sns_info.homepage_url if sns_info else None
        )
        
        # 운영 시간 정보 조회
        operation_infos = await operation_repo.get_by_store_id(store_id)
        operation_data = [
            StoreOperationResponse(
                day_of_week=info.day_of_week,
                open_time=info.open_time,
                close_time=info.close_time,
                pickup_start_time=info.pickup_start_time,
                pickup_end_time=info.pickup_end_time,
                is_open_enabled=info.is_open_enabled
            )
            for info in sorted(operation_infos, key=lambda x: x.day_of_week)
        ]
        
        # 이미지 정보 조회
        store_images = await image_repo.get_by_store_id(store_id)
        image_data = [
            ImageUploadResponse(
                store_image_id=img.store_image_id,
                image_url=img.image_url,
                display_order=img.display_order,
                created_at=img.created_at,
                updated_at=img.updated_at
            )
            for img in sorted(store_images, key=lambda x: x.display_order)
        ]
        
        # 상품 정보 조회
        products = await product_repo.get_all_by_store_id(store_id)
        product_data = [
            ProductResponse(
                product_id=prod.product_id,
                product_name=prod.product_name,
                original_price=prod.original_price,
                sale_rate=prod.sale_rate,
                sale_price=prod.sale_price,
                product_description=prod.product_description,
                product_image_url=prod.product_image_url,
                stock_quantity=prod.stock_quantity,
                is_enabled=prod.is_enabled,
                pickup_start_time=prod.pickup_start_time,
                pickup_end_time=prod.pickup_end_time,
                created_at=prod.created_at,
                updated_at=prod.updated_at
            )
            for prod in products
        ]
        
        return StoreDetailResponse(
            store_id=store.store_id,
            store_name=store.store_name,
            store_introduction=store.store_introduction,
            store_phone=store.store_phone,
            seller_email=store.seller_email,
            created_at=store.created_at,
            address=address_data,
            sns=sns_data,
            operation_times=operation_data,
            images=image_data,
            products=product_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"가게 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )