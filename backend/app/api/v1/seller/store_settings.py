from typing import List
from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep,
    AddressRepositoryDep,
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


@router.put("/{store_id}/address", response_model=StoreAddressResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_address(
    store_id: str,
    request: StoreAddressUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    address_repo: AddressRepositoryDep
):
    """
    매장 주소 수정
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        # 현재 가게 정보 조회
        store = await store_repo.get_by_store_id(store_id)
        
        if store.address_id:
            await address_repo.update(
                store.address_id,
                sido=request.sido,
                sigungu=request.sigungu,
                bname=request.bname,
                lat=request.lat,
                lng=request.lng
            )
        
        await store_repo.update(
            store_id,
            store_postal_code=request.postal_code,
            store_address=request.address,
            store_detail_address=request.detail_address
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


@router.put("/{store_id}/payment", response_model=StorePaymentResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def update_store_payment(
    store_id: str,
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
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
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

@router.patch("/{store_id}/operation/day/{day_of_week}", response_model=StoreOperationResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 수정할 권한이 없음",
        404: ["가게를 찾을 수 없음", "해당 요일 운영 정보를 찾을 수 없음"],
        422: "잘못된 요일 값"
    })
)
async def update_store_day_operation(
    store_id: str,
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
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    if not 0 <= day_of_week <= 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="요일은 0(월요일)부터 6(일요일) 사이의 값이어야 합니다."
        )
    
    try:
        # 해당 요일 운영 정보 조회
        operation_info = await operation_repo.get_by_store_and_day(store_id, day_of_week)
        
        if not operation_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 요일의 운영 정보를 찾을 수 없습니다."
            )
        
        update_data = {
            "is_open_enabled": request.is_open_enabled,
            "open_time": request.open_time,
            "close_time": request.close_time,
            "pickup_start_time": request.pickup_start_time,
            "pickup_end_time": request.pickup_end_time
        }
        
        # 운영 정보 업데이트
        await operation_repo.update(
            operation_info.operation_id,
            **update_data
        )
        
        # 업데이트된 정보 조회
        updated_info = await operation_repo.get_by_store_and_day(store_id, day_of_week)
        
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


@router.get("/{store_id}/operation", response_model=List[StoreOperationResponse],
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 정보를 조회할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_operation(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep
):
    """
    운영 정보 조회
    
    모든 요일의 운영 정보를 조회합니다.
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
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