from typing import List
from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses

from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    StoreRepositoryDep, 
    StoreProductInfoRepositoryDep
)
from schemas.product import ProductsResponse, ProductResponse
from schemas.store import StoreDetailResponse
from schemas.store_operation import StoreOperationResponse
from schemas.image import ImageUploadResponse
from core.object_storage import object_storage

router = APIRouter(prefix="/search", tags=["Customer-Search"])


@router.get("/stores", response_model=List[StoreDetailResponse],
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_stores(
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep
):
    """
    가게 및 상품 정보 조회 API
    
    상품이 등록된 가게들의 상세 정보(주소, SNS, 운영시간, 이미지, 상품)를 조회
    상품이 없는 가게는 조회 결과에서 제외
    """
    
    stores = await store_repo.get_stores_with_products()
    
    if not stores:
        return []
    
    result = []
    
    for store in stores:
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
            "lng": store.address.lng
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
        
        result.append(StoreDetailResponse(**store_data))
    
    return result


@router.get("/stores/{store_id}/products", response_model=ProductsResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"가게를 찾을 수 없음"
    })             
)
async def get_store_products(
    store_id: str,
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
):
    """
    가게 상품 조회 API
    
    특정 가게의 모든 상품 정보를 상세하게 조회
    """
    
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    products = await product_repo.get_by_store_with_nutrition(store_id)
    
    product_list = []
    for product in products:
        nutrition_types = [info.nutrition_type for info in product.nutrition_info] if product.nutrition_info else []
        
        product_list.append(
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
    
    return ProductsResponse(
        store_id=store.store_id,
        store_name=store.store_name,
        products=product_list
    )