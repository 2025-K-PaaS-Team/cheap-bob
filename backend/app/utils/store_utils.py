from fastapi import HTTPException, status

from api.deps.repository import StoreRepositoryDep
from services.redis_cache import RedisCache
from schemas.product import ProductResponse
from schemas.store import StoreDetailResponseForCustomer
from schemas.store_operation import StoreOperationResponse
from schemas.image import ImageUploadResponse
from core.object_storage import object_storage


async def get_store_id_by_email(
    seller_email: str,
    store_repo: StoreRepositoryDep
) -> str:
    """
    seller_email로 store_id 조회 (Redis 캐싱 적용)
    
    Args:
        seller_email: 현재 로그인한 판매자 이메일
        store_repo: 가게 레포지토리
    
    Returns:
        str: store_id
    
    Raises:
        HTTPException: 가게를 찾을 수 없는 경우
    """
    # Redis에서 캐시된 store_id 조회
    cached_store_id = await RedisCache.get_store_id(seller_email)
    
    if cached_store_id:
        return cached_store_id
    
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
    
    return store.store_id


def convert_store_to_response(store, is_favorite: bool = False) -> StoreDetailResponseForCustomer:
    """가게 정보를 StoreDetailResponseForCustomer로 변환하는 헬퍼 함수"""
    # 가게 기본 정보
    store_data = {
        "store_id": store.store_id,
        "store_name": store.store_name,
        "store_introduction": store.store_introduction,
        "store_phone": store.store_phone,
        "seller_email": store.seller_email,
        "created_at": store.created_at
    }
    
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
    store_data["products"] = product_responses
    
    # 주소 정보
    store_data["address"] = {
        "store_id": store.store_id,
        "postal_code": store.store_postal_code,
        "address": store.store_address,
        "detail_address": store.store_detail_address,
        "sido": store.address.sido,
        "sigungu": store.address.sigungu,
        "bname": store.address.bname,
        "lat": store.address.lat,
        "lng": store.address.lng,
        "nearest_station": store.address.nearest_station,
        "walking_time": store.address.walking_time
    }
    
    # SNS 정보
    if store.sns_info:
        store_data["sns"] = {
            "instagram": store.sns_info.instagram,
            "facebook": store.sns_info.facebook,
            "x": store.sns_info.x,
            "homepage": store.sns_info.homepage
        }
    
    # 운영 시간 정보
    store_data["operation_times"] = [
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
    store_data["images"] = image_responses
    
    store_data["is_favorite"] = is_favorite
    return StoreDetailResponseForCustomer(**store_data)