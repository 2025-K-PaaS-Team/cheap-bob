from typing import Annotated, Optional, Literal
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import HttpUrl

from utils.docs_error import create_error_responses
from api.deps import CurrentSellerDep, AsyncSessionDep
from repositories.store import StoreRepository
from repositories.store_sns import StoreSNSRepository
from schemas.store_sns import (
    StoreSNSUpdateRequest,
    StoreSNSResponse
)

router = APIRouter(prefix="/store/sns", tags=["Seller-Store-SNS"])

SNSType = Literal["instagram", "facebook", "x", "homepage"]


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_store_sns_repository(session: AsyncSessionDep) -> StoreSNSRepository:
    return StoreSNSRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
StoreSNSRepositoryDep = Annotated[StoreSNSRepository, Depends(get_store_sns_repository)]


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


@router.get("/{store_id}", response_model=StoreSNSResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 조회할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_sns(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    sns_repo: StoreSNSRepositoryDep
):
    """
    가게 SNS 정보 조회
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        sns_info = await sns_repo.get_by_store_id(store_id)
        
        if not sns_info:
            return StoreSNSResponse(
                store_id=store_id,
                instagram=None,
                facebook=None,
                x=None,
                homepage=None
            )
        
        return StoreSNSResponse(
            store_id=store_id,
            instagram=HttpUrl(sns_info.instagram) if sns_info.instagram else None,
            facebook=HttpUrl(sns_info.facebook) if sns_info.facebook else None,
            x=HttpUrl(sns_info.x) if sns_info.x else None,
            homepage=HttpUrl(sns_info.homepage) if sns_info.homepage else None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SNS 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{store_id}", response_model=StoreSNSResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: ["가게를 찾을 수 없음", "등록된 SNS 정보를 찾을 수 없음"]
    })
)
async def update_store_sns(
    store_id: str,
    request: StoreSNSUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    sns_repo: StoreSNSRepositoryDep
):
    """
    가게 SNS 정보 수정
    
    기존 SNS 정보를 수정합니다.
    특정 SNS만 수정하려면 해당 필드만 포함해서 요청하세요.
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        # 기존 SNS 정보 확인
        existing_sns = await sns_repo.get_by_store_id(store_id)
        if not existing_sns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록된 SNS 정보를 찾을 수 없습니다. 먼저 POST 메서드로 등록해주세요."
            )
        
        # 업데이트할 데이터 준비
        update_data = {}
        if request.instagram is not None:
            update_data["instagram"] = str(request.instagram) if request.instagram else None
        if request.facebook is not None:
            update_data["facebook"] = str(request.facebook) if request.facebook else None
        if request.x is not None:
            update_data["x"] = str(request.x) if request.x else None
        if request.homepage is not None:
            update_data["homepage"] = str(request.homepage) if request.homepage else None
        
        # SNS 정보 업데이트
        await sns_repo.update_where({"store_id":store_id}, **update_data)
        
        # 업데이트된 정보 조회
        updated_sns = await sns_repo.get_by_store_id(store_id)
        
        return StoreSNSResponse(
            store_id=store_id,
            instagram=HttpUrl(updated_sns.instagram) if updated_sns.instagram else None,
            facebook=HttpUrl(updated_sns.facebook) if updated_sns.facebook else None,
            x=HttpUrl(updated_sns.x) if updated_sns.x else None,
            homepage=HttpUrl(updated_sns.homepage) if updated_sns.homepage else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SNS 정보 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{store_id}/{sns_type}", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: ["가게를 찾을 수 없음", "등록된 SNS 정보를 찾을 수 없음"],
        422: "잘못된 SNS 유형"
    })
)
async def delete_store_sns_by_type(
    store_id: str,
    sns_type: SNSType,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    sns_repo: StoreSNSRepositoryDep
):
    """
    특정 SNS 정보 삭제
    
    특정 SNS 유형의 URL만 삭제합니다.
    - sns_type: instagram, facebook, x, homepage 중 하나
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        # 기존 SNS 정보 확인
        existing_sns = await sns_repo.get_by_store_id(store_id)
        if not existing_sns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록된 SNS 정보를 찾을 수 없습니다."
            )
        
        # 해당 SNS 타입의 URL을 None으로 설정
        update_data = {sns_type: None}
        await sns_repo.update_where({"store_id":store_id}, **update_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SNS 정보 삭제 중 오류가 발생했습니다: {str(e)}"
        )