from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep
from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.seller.schema.store import PaginatedStoreResponse
from app.domain.seller.schema.product import ProductsResponse
from app.domain.customer.service.customer_search import CustomerSearchService
from app.domain.customer.service.customer_history import CustomerHistoryService
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/search", tags=["Customer-Search"])


@router.get(
    "/stores",
    response_model=PaginatedStoreResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_stores(
    current_user: CurrentCustomerDep,
    page: int = Query(0, description="페이지 번호", ge=0),
    search_service: CustomerSearchService = Depends(Provide["customer_search_service"]),
):
    """상품이 등록된 가게들의 상세 정보를 페이지 단위로 조회."""
    return await search_service.list_stores(
        customer_email=current_user["sub"], page=page,
    )


@router.get(
    "/stores/{store_id}/products",
    response_model=ProductsResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음"],
    }),
)
@inject
async def get_store_products(
    store_id: str,
    current_user: CurrentCustomerDep,
    search_service: CustomerSearchService = Depends(Provide["customer_search_service"]),
):
    """특정 가게의 모든 상품 + 영양 정보."""
    try:
        return await search_service.get_store_products(store_id)
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/stores/by-location",
    response_model=PaginatedStoreResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def search_stores_by_location(
    current_user: CurrentCustomerDep,
    sido: str = Query(..., description="시/도"),
    sigungu: str = Query(..., description="시/군/구"),
    bname: List[str] = Query(..., description="읍/면/동 리스트"),
    page: int = Query(0, ge=0),
    search_service: CustomerSearchService = Depends(Provide["customer_search_service"]),
):
    return await search_service.search_by_location(
        customer_email=current_user["sub"],
        sido=sido,
        sigungu=sigungu,
        bname=bname,
        page=page,
    )


@router.get(
    "/stores/by-name",
    response_model=PaginatedStoreResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def search_stores_by_name(
    current_user: CurrentCustomerDep,
    search_name: str = Query(..., description="검색할 가게/상품 이름"),
    page: int = Query(0, ge=0),
    search_service: CustomerSearchService = Depends(Provide["customer_search_service"]),
    history_service: CustomerHistoryService = Depends(
        Provide["customer_history_service"],
    ),
):
    customer_email = current_user["sub"]
    response = await search_service.search_by_name(
        customer_email=customer_email, search_name=search_name, page=page,
    )
    # 히스토리 기록은 RDB 트랜잭션 밖 (Redis) 이므로 라우터에서 호출한다.
    await history_service.record_search(customer_email, search_name)
    return response


@router.get(
    "/stores/by-location-name",
    response_model=PaginatedStoreResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def search_stores_by_location_name(
    current_user: CurrentCustomerDep,
    sido: str = Query(..., description="시/도"),
    sigungu: str = Query(..., description="시/군/구"),
    bname: List[str] = Query(..., description="읍/면/동 리스트"),
    search_name: str = Query(..., description="검색할 가게/상품 이름"),
    page: int = Query(0, ge=0),
    search_service: CustomerSearchService = Depends(Provide["customer_search_service"]),
    history_service: CustomerHistoryService = Depends(
        Provide["customer_history_service"],
    ),
):
    customer_email = current_user["sub"]
    response = await search_service.search_by_location_and_name(
        customer_email=customer_email,
        sido=sido,
        sigungu=sigungu,
        bname=bname,
        search_name=search_name,
        page=page,
    )
    await history_service.record_search(customer_email, search_name)
    return response
