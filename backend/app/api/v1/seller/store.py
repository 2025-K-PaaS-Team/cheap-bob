from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentSellerDep
from api.deps.repository import StoreRepositoryDep
from schemas.store import StoreDetailResponse, StoreSNSInfo
from schemas.product import ProductResponse
from schemas.image import ImageUploadResponse
from schemas.store_operation import StoreOperationResponse
from schemas.store_settings import StoreAddressResponse
from services.redis_cache import RedisCache
from core.object_storage import object_storage

router = APIRouter(prefix="/store", tags=["Seller-Store"])

async def get_store_id_by_email(
    seller_email: str,
    store_repo: StoreRepositoryDep
) -> tuple[str, object]:
    """
    seller_email로 store_id 조회 (Redis 캐싱 적용)
    
    Args:
        seller_email: 현재 로그인한 판매자 이메일
        store_repo: 가게 레포지토리
    
    Returns:
        tuple: (store_id, store 객체)
    
    Raises:
        HTTPException: 가게를 찾을 수 없는 경우
    """
    # Redis에서 캐시된 store_id 조회
    cached_store_id = await RedisCache.get_store_id(seller_email)
    
    if cached_store_id:
        # Redis에 캐시된 경우, DB에서 모든 관련 정보와 함께 store 조회
        store = await store_repo.get_with_full_info(cached_store_id)
        if store:
            return cached_store_id, store
    
    # Redis에 없거나 DB에서 찾을 수 없는 경우, seller_email로 직접 조회
    stores = await store_repo.get_by_seller_email(seller_email)
    
    if not stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    
    # 첫 번째 가게 사용 - (현재 버전은 판매자가 하나의 가게만 가짐)
    store = stores[0]
    
    # Redis에 캐싱
    await RedisCache.set_store_id(seller_email, store.store_id)
    
    # 모든 관련 정보와 함께 다시 조회
    store = await store_repo.get_with_full_info(store.store_id)
    
    return store.store_id, store

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
    
    # seller_email로 store_id 조회 (Redis 캐싱 적용)
    store_id, store = await get_store_id_by_email(seller_email, store_repo)

    try:
        # store 객체를 StoreDetailResponse로 변환
        
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
            lng=store.address.lng
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