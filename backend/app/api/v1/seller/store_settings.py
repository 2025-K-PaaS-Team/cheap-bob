from typing import List
from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep,
    StorePaymentInfoRepositoryDep,
    StoreOperationInfoRepositoryDep
)
from schemas.store_settings import (
    StoreAddressUpdateRequest,
    StorePaymentUpdateRequest,
    StoreDayOperationUpdateRequest,
    StoreAddressResponse,
    StorePaymentResponse,
    StoreOperationResponse
)

router = APIRouter(prefix="/store/settings", tags=["Seller-Store-Settings"])


@router.put("/address", response_model=StoreAddressResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_address(
    request: StoreAddressUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    매장 주소 수정
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    try:
        # 업데이트
        store = await store_repo.update_store_and_address_atomic(
            store_id=store_id,
            postal_code=request.postal_code,
            address=request.address,
            detail_address=request.detail_address,
            sido=request.sido,
            sigungu=request.sigungu,
            bname=request.bname,
            lat=request.lat,
            lng=request.lng
        )
        
        if not store:
            raise HTTPException(
                status_code=404,
                detail="가게를 찾을 수 없습니다"
            )
        
        return StoreAddressResponse(
            store_id=store_id,
            postal_code=request.postal_code,
            address=request.address,
            detail_address=request.detail_address,
            sido=request.sido,
            sigungu=request.sigungu,
            bname=request.bname,
            lat=request.lat,
            lng=request.lng
        )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주소 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/payment", response_model=StorePaymentResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_payment(
    request: StorePaymentUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    payment_repo: StorePaymentInfoRepositoryDep
):
    """
    결제 정보 수정
    
    포트원 연동 정보를 수정합니다.
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    try:
        await payment_repo.update_portone_info(
            store_id=store_id,
            portone_store_id=request.portone_store_id,
            portone_channel_id=request.portone_channel_id,
            portone_secret_key=request.portone_secret_key
        )
        
        return StorePaymentResponse(
            store_id=store_id,
            portone_store_id=request.portone_store_id,
            portone_channel_id=request.portone_channel_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결제 정보 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/operation", response_model=List[StoreOperationResponse],
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_operation(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep
):
    """
    운영 정보 조회
    
    모든 요일의 운영 정보를 조회합니다.
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    try:
        operation_infos = await operation_repo.get_by_store_id(store_id)
        
        return [
            StoreOperationResponse(
                day_of_week=info.day_of_week,
                open_time=info.open_time,
                close_time=info.close_time,
                pickup_start_time=info.pickup_start_time,
                pickup_end_time=info.pickup_end_time,
                is_open_enabled=info.is_open_enabled
            )
            for info in sorted(operation_infos, key=lambda x: x.day_of_week)
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"운영 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/operation/day/{day_of_week}", response_model=StoreOperationResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "해당 요일 운영 정보를 찾을 수 없음"],
        422: "잘못된 요일 값"
    })
)
async def update_store_day_operation(
    day_of_week: int,
    request: StoreDayOperationUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep
):
    """
    특정 요일 운영 정보 수정
    
    특정 요일의 운영 정보만 수정합니다.
    
    - day_of_week: 0(월요일) ~ 6(일요일)
    - 비활성화 시: is_open_enabled를 false로만 설정
    - 활성화 시: 모든 시간 정보 필수
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    if not 0 <= day_of_week <= 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="요일은 0(월요일)부터 6(일요일) 사이의 값이어야 합니다."
        )
    
    try:
        # 업데이트
        updated_info = await operation_repo.update_and_return_by_store_and_day(
            store_id=store_id,
            day_of_week=day_of_week,
            is_open_enabled=request.is_open_enabled,
            open_time=request.open_time,
            close_time=request.close_time,
            pickup_start_time=request.pickup_start_time,
            pickup_end_time=request.pickup_end_time
        )
        
        if not updated_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 요일의 운영 정보를 찾을 수 없습니다."
            )
        
        return StoreOperationResponse(
            day_of_week=updated_info.day_of_week,
            open_time=updated_info.open_time,
            close_time=updated_info.close_time,
            pickup_start_time=updated_info.pickup_start_time,
            pickup_end_time=updated_info.pickup_end_time,
            is_open_enabled=updated_info.is_open_enabled
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"운영 정보 수정 중 오류가 발생했습니다: {str(e)}"
        )