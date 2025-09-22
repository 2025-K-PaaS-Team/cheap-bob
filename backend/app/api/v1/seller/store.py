from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import StoreRepositoryDep
from schemas.store import StoreDetailResponse, StoreSNSInfo
from schemas.product import ProductResponse
from schemas.image import ImageUploadResponse
from schemas.store_operation import StoreOperationResponse
from schemas.store_settings import StoreAddressResponse
from core.object_storage import object_storage

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