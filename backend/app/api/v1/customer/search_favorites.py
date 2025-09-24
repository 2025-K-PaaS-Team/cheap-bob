from typing import List
from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.store_utils import convert_store_to_response

from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    StoreRepositoryDep, 
    CustomerFavoriteRepositoryDep
)
from schemas.store import StoreDetailResponseForCustomer, StoreFavoriteStateResponse

router = APIRouter(prefix="/search", tags=["Customer-Search"])


@router.get("/stores/favorites", response_model=List[StoreDetailResponseForCustomer],
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_favorite_stores(
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep
):
    """
    즐겨찾기 가게 목록 조회 API
    
    고객이 즐겨찾기한 모든 가게들의 상세 정보를 조회
    """
    
    stores = await store_repo.get_favorite_stores_with_full_info(current_user["sub"])
    
    if not stores:
        return []
    
    return [convert_store_to_response(store, is_favorite=True) for store in stores]


@router.post("/stores/{store_id}/favorites", response_model=StoreFavoriteStateResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"가게를 찾을 수 없음",
        409:"이미 즐겨찾기에 등록된 가게"
    })
)
async def add_favorite_store(
    store_id: str,
    current_user: CurrentCustomerDep,
    favorite_repo: CustomerFavoriteRepositoryDep,
    store_repo: StoreRepositoryDep
):
    """
    즐겨찾기 가게 등록 API
    
    특정 가게를 고객의 즐겨찾기에 추가
    """
    
    # 가게 존재 확인
    store = await store_repo.get_by_store_id(store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    # 이미 즐겨찾기인지 확인
    existing = await favorite_repo.get_by_customer_and_store(current_user["sub"], store_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 즐겨찾기에 등록된 가게입니다"
        )
    
    # 즐겨찾기 추가
    await favorite_repo.create_for_customer(current_user["sub"], store_id)
    
    return StoreFavoriteStateResponse(message="즐겨찾기에 추가되었습니다")


@router.delete("/stores/{store_id}/favorites", response_model=StoreFavoriteStateResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"즐겨찾기에서 찾을 수 없음"
    })
)
async def remove_favorite_store(
    store_id: str,
    current_user: CurrentCustomerDep,
    favorite_repo: CustomerFavoriteRepositoryDep
):
    """
    즐겨찾기 가게 삭제 API
    
    고객의 즐겨찾기에서 특정 가게를 삭제
    """
    
    # 즐겨찾기 삭제
    deleted = await favorite_repo.delete_for_customer(current_user["sub"], store_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="즐겨찾기에서 찾을 수 없습니다"
        )
        
    return StoreFavoriteStateResponse(message="즐겨찾기가 삭제 되었습니다")