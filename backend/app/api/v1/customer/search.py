from fastapi import APIRouter, HTTPException, status, Query

from utils.docs_error import create_error_responses
from utils.store_utils import convert_store_to_response

from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    StoreRepositoryDep, 
    StoreProductInfoRepositoryDep
)
from schemas.product import ProductsResponse, ProductResponse
from schemas.store import PaginatedStoreResponse
from services.redis_cache import SearchHistoryCache

router = APIRouter(prefix="/search", tags=["Customer-Search"])


@router.get("/stores", response_model=PaginatedStoreResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_stores(
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep,
    page: int = Query(0, description="페이지 번호", ge=0)
):
    """
    가게 및 상품 정보 조회 API
    
    상품이 등록된 가게들의 상세 정보(주소, SNS, 운영시간, 이미지, 상품)를 조회
    상품이 없는 가게는 조회 결과에서 제외
    """
    customer_email = current_user["sub"]

    items_per_page = 4
    offset = page * items_per_page
    
    store_results, is_end = await store_repo.get_stores_with_products_and_favorites(
        customer_email, offset=offset, limit=items_per_page
    )
    
    stores = [convert_store_to_response(store, is_favorite) for store, is_favorite in store_results]
    
    return PaginatedStoreResponse(stores=stores, is_end=is_end)


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


@router.get("/stores/by-location", response_model=PaginatedStoreResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def search_stores_by_location(
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep,
    sido: str = Query(..., description="시/도"),
    sigungu: str = Query(..., description="시/군/구"),
    bname: str = Query(..., description="읍/면/동"),
    page: int = Query(0, description="페이지 번호", ge=0)
):
    """
    위치로만 가게 검색 API
    
    지정된 주소(시/도, 시/군/구, 읍/면/동)에 위치한 모든 가게들을 조회
    """
    customer_email = current_user["sub"]
    
    items_per_page = 4
    offset = page * items_per_page
    
    store_results, is_end = await store_repo.search_by_location_with_favorites(
        sido=sido,
        sigungu=sigungu,
        bname=bname,
        customer_email=customer_email,
        offset=offset,
        limit=items_per_page
    )

    stores = [convert_store_to_response(store, is_favorite) for store, is_favorite in store_results]
    
    return PaginatedStoreResponse(stores=stores, is_end=is_end)


@router.get("/stores/by-name", response_model=PaginatedStoreResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def search_stores_by_name(
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep,
    search_name: str = Query(..., description="검색할 가게 또는 상품 이름"),
    page: int = Query(0, description="페이지 번호", ge=0)
):
    """
    가게/상품 이름으로 검색 API
    
    검색어가 가게 이름이나 상품 이름에 포함된 가게들을 조회
    """
    customer_email = current_user["sub"]
    
    items_per_page = 4
    offset = page * items_per_page
    
    store_results, is_end = await store_repo.search_by_name_with_favorites(
        search_name, customer_email, offset=offset, limit=items_per_page
    )
    
    await SearchHistoryCache.add_search_name(customer_email, search_name)
    
    stores = [convert_store_to_response(store, is_favorite) for store, is_favorite in store_results]
    
    return PaginatedStoreResponse(stores=stores, is_end=is_end)


@router.get("/stores/by-location-name", response_model=PaginatedStoreResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def search_stores_by_location_name(
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep,
    sido: str = Query(..., description="시/도"),
    sigungu: str = Query(..., description="시/군/구"),
    bname: str = Query(..., description="읍/면/동"),
    search_name: str = Query(..., description="검색할 가게 또는 상품 이름"),
    page: int = Query(0, description="페이지 번호", ge=0)
):
    """
    주소와 가게/상품 이름으로 검색 API
    
    지정된 주소(시/도, 시/군/구, 읍/면/동)에 위치하고 
    검색어가 가게 이름 또는 상품 이름에 포함된 가게들을 조회
    """
    customer_email = current_user["sub"]
    
    items_per_page = 4
    offset = page * items_per_page
    
    store_results, is_end = await store_repo.search_by_location_and_name_with_favorites(
        sido=sido,
        sigungu=sigungu,
        bname=bname,
        search_name=search_name,
        customer_email=customer_email,
        offset=offset,
        limit=items_per_page
    )
    
    await SearchHistoryCache.add_search_name(customer_email, search_name)
    
    stores = [convert_store_to_response(store, is_favorite) for store, is_favorite in store_results]
    
    return PaginatedStoreResponse(stores=stores, is_end=is_end)