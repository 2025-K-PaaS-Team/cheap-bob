from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, status
from pydantic import HttpUrl

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import StoreRepositoryDep, StoreSNSRepositoryDep
from schemas.store_sns import (
    StoreSNSUpdateRequest,
    StoreSNSResponse
)

router = APIRouter(prefix="/store/sns", tags=["Seller-Store-SNS"])

SNSType = Literal["instagram", "facebook", "x", "homepage"]


@router.get("", response_model=StoreSNSResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_sns(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    sns_repo: StoreSNSRepositoryDep
):
    """
    가게 SNS 정보 조회
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
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


@router.put("", response_model=StoreSNSResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "등록된 SNS 정보를 찾을 수 없음"]
    })
)
async def update_store_sns(
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
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
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


@router.delete("/{sns_type}", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "등록된 SNS 정보를 찾을 수 없음"],
        422: "잘못된 SNS 유형"
    })
)
async def delete_store_sns_by_type(
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
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
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