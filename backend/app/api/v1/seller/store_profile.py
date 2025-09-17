from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentSellerDep
from api.deps.database import AsyncSessionDep
from repositories.store import StoreRepository
from schemas.seller_profile import (
    StoreNameUpdateRequest,
    StoreIntroductionUpdateRequest,
    StorePhoneUpdateRequest,
    StoreProfileResponse
)

router = APIRouter(prefix="/store/profile", tags=["Seller-Store-Profile"])


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]


async def verify_store_owner(
    store_id: str,
    seller_email: str,
    store_repo: StoreRepositoryDep
) -> None:
    """
    가게 소유권 검증
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
            detail="가게 정보를 수정할 권한이 없습니다."
        )


@router.put("/{store_id}/name", response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_name(
    store_id: str,
    request: StoreNameUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    매장 이름 수정
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        # 이름 업데이트
        updated_store = await store_repo.update(
            store_id,
            store_name=request.store_name
        )
        
        return StoreProfileResponse(
            store_id=updated_store.store_id,
            store_name=updated_store.store_name,
            store_introduction=updated_store.store_introduction,
            store_phone=updated_store.store_phone
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"매장 이름 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{store_id}/introduction", response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_introduction(
    store_id: str,
    request: StoreIntroductionUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    매장 설명 수정
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        # 설명 업데이트
        updated_store = await store_repo.update(
            store_id,
            store_introduction=request.store_introduction
        )
        
        return StoreProfileResponse(
            store_id=updated_store.store_id,
            store_name=updated_store.store_name,
            store_introduction=updated_store.store_introduction,
            store_phone=updated_store.store_phone
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"매장 설명 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{store_id}/phone", response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: "가게를 찾을 수 없음",
        422: "유효하지 않은 전화번호 형식"
    })
)
async def update_store_phone(
    store_id: str,
    request: StorePhoneUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    매장 전화번호 수정
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        # 전화번호 업데이트
        updated_store = await store_repo.update(
            store_id,
            store_phone=request.store_phone
        )
        
        return StoreProfileResponse(
            store_id=updated_store.store_id,
            store_name=updated_store.store_name,
            store_introduction=updated_store.store_introduction,
            store_phone=updated_store.store_phone
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"매장 전화번호 수정 중 오류가 발생했습니다: {str(e)}"
        )