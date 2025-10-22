from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep, CurrentSellerNoActiveDep
from api.deps.repository import StoreRepositoryDep
from schemas.seller_profile import (
    StoreNameUpdateRequest,
    StoreIntroductionUpdateRequest,
    StorePhoneUpdateRequest,
    StoreProfileResponse
)
from schemas.me import UserProfileMeResponse

router = APIRouter(prefix="/store/profile", tags=["Seller-Store-Profile"])

@router.get(
    "/me",
    response_model=UserProfileMeResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_customer_profile_all(
    current_user: CurrentSellerNoActiveDep
):
    """소비자 이메일 조회"""
    seller_email = current_user["sub"]
    
    return UserProfileMeResponse(email=seller_email)

@router.put("/name", response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_name(
    request: StoreNameUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    매장 이름 수정
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
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


@router.put("/introduction", response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_introduction(
    request: StoreIntroductionUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    매장 설명 수정
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
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


@router.put("/phone", response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        422: "유효하지 않은 전화번호 형식"
    })
)
async def update_store_phone(
    request: StorePhoneUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    매장 전화번호 수정
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
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