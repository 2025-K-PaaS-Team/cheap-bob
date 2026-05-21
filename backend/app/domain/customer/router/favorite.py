from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep
from app.domain.seller.schema.store import StoreDetailResponseForCustomer, StoreFavoriteStateResponse
from app.domain.customer.service.exception import (
    FavoriteAlreadyExistsError,
    FavoriteNotFoundError,
    StoreNotFoundError,
)
from app.domain.customer.service.customer_search import CustomerSearchService
from app.domain.customer.service.customer_favorite import CustomerFavoriteService
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/search", tags=["Customer-Search"])


@router.get(
    "/stores/favorites",
    response_model=List[StoreDetailResponseForCustomer],
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_favorite_stores(
    current_user: CurrentCustomerDep,
    search_service: CustomerSearchService = Depends(Provide["customer_search_service"]),
):
    """즐겨찾기한 모든 가게의 상세 정보."""
    return await search_service.list_favorite_stores(current_user["sub"])


@router.post(
    "/stores/{store_id}/favorites",
    response_model=StoreFavoriteStateResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음"],
        409: ["이미 즐겨찾기에 등록된 가게"],
    }),
)
@inject
async def add_favorite_store(
    store_id: str,
    current_user: CurrentCustomerDep,
    favorite_service: CustomerFavoriteService = Depends(
        Provide["customer_favorite_service"],
    ),
):
    try:
        await favorite_service.add(
            customer_email=current_user["sub"], store_id=store_id,
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FavoriteAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return StoreFavoriteStateResponse(message="즐겨찾기에 추가되었습니다")


@router.delete(
    "/stores/{store_id}/favorites",
    response_model=StoreFavoriteStateResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["즐겨찾기에서 찾을 수 없음"],
    }),
)
@inject
async def remove_favorite_store(
    store_id: str,
    current_user: CurrentCustomerDep,
    favorite_service: CustomerFavoriteService = Depends(
        Provide["customer_favorite_service"],
    ),
):
    try:
        await favorite_service.remove(
            customer_email=current_user["sub"], store_id=store_id,
        )
    except FavoriteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return StoreFavoriteStateResponse(message="즐겨찾기가 삭제 되었습니다")
