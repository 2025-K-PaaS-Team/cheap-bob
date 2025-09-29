from typing import List
from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep,
    StorePaymentInfoRepositoryDep,
    StoreOperationInfoRepositoryDep,
    StoreOperationInfoModificationRepositoryDep
)
from schemas.store_settings import (
    StoreAddressUpdateRequest,
    StorePaymentUpdateRequest,
    StoreAddressResponse,
    StorePaymentResponse,
    StoreOperationResponse,
    StoreOperationReservationRequest,
    StoreOperationReservationUpdateRequest,
    StoreOperationReservationResponse,
    StoreOperationModificationResponse
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
            portone_channel_id=request.portone_channel_id
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


@router.post("/operation/reservation", response_model=StoreOperationReservationResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        400: ["이미 예약이 존재함", "시간 설정이 올바르지 않음"]
    })
)
async def create_operation_reservation(
    request: StoreOperationReservationRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_modification_repo: StoreOperationInfoModificationRepositoryDep
):
    """
    운영 정보 변경 예약 추가
    
    다음 날 적용될 운영 정보 변경을 예약합니다.
    월요일부터 일요일까지 모든 요일의 정보를 포함해야 합니다.
    """
    seller_email = current_user["sub"]
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    try:
        modifications_data = [
            {
                'day_of_week': op.day_of_week,
                'open_time': op.open_time,
                'close_time': op.close_time,
                'pickup_start_time': op.pickup_start_time,
                'pickup_end_time': op.pickup_end_time,
                'is_open_enabled': op.is_open_enabled
            }
            for op in request.operation_times
        ]
        
        modifications = await operation_modification_repo.create_modifications_batch(
            store_id=store_id,
            modifications_data=modifications_data
        )
        
        # Response 형식으로 변환
        modification_responses = [
            StoreOperationModificationResponse(
                modification_id=mod.modification_id,
                operation_id=mod.operation_id,
                day_of_week=mod.operation_info.day_of_week,
                new_open_time=mod.new_open_time,
                new_close_time=mod.new_close_time,
                new_pickup_start_time=mod.new_pickup_start_time,
                new_pickup_end_time=mod.new_pickup_end_time,
                new_is_open_enabled=mod.new_is_open_enabled,
                created_at=mod.created_at
            )
            for mod in sorted(modifications, key=lambda x: x.operation_info.day_of_week)
        ]
        
        return StoreOperationReservationResponse(modifications=modification_responses)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"운영 정보 예약 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/operation/reservation", response_model=StoreOperationReservationResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def get_operation_reservation(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_modification_repo: StoreOperationInfoModificationRepositoryDep
):
    """
    운영 정보 변경 예약 조회
    
    현재 예약된 운영 정보 변경사항을 조회합니다.
    """
    seller_email = current_user["sub"]
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    try:
        modifications = await operation_modification_repo.get_by_store_id(store_id)
        
        modification_responses = [
            StoreOperationModificationResponse(
                modification_id=mod.modification_id,
                operation_id=mod.operation_id,
                day_of_week=mod.operation_info.day_of_week,
                new_open_time=mod.new_open_time,
                new_close_time=mod.new_close_time,
                new_pickup_start_time=mod.new_pickup_start_time,
                new_pickup_end_time=mod.new_pickup_end_time,
                new_is_open_enabled=mod.new_is_open_enabled,
                created_at=mod.created_at
            )
            for mod in sorted(modifications, key=lambda x: x.operation_info.day_of_week)
        ]
        
        return StoreOperationReservationResponse(modifications=modification_responses)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"운영 정보 예약 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/operation/reservation", response_model=StoreOperationReservationResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "예약을 찾을 수 없음"],
        400: "시간 설정이 올바르지 않음"
    })
)
async def update_operation_reservation(
    request: StoreOperationReservationUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_modification_repo: StoreOperationInfoModificationRepositoryDep
):
    """
    운영 정보 변경 예약 수정
    
    예약된 운영 정보 변경사항을 수정합니다.
    월요일부터 일요일까지 모든 요일의 정보를 포함해야 합니다.
    """
    seller_email = current_user["sub"]
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    try:
        modifications_data = [
            {
                'day_of_week': op.day_of_week,
                'open_time': op.open_time,
                'close_time': op.close_time,
                'pickup_start_time': op.pickup_start_time,
                'pickup_end_time': op.pickup_end_time,
                'is_open_enabled': op.is_open_enabled
            }
            for op in request.operation_times
        ]
        
        modifications = await operation_modification_repo.update_modifications_batch(
            store_id=store_id,
            modifications_data=modifications_data
        )
        
        modification_responses = [
            StoreOperationModificationResponse(
                modification_id=mod.modification_id,
                operation_id=mod.operation_id,
                day_of_week=mod.operation_info.day_of_week,
                new_open_time=mod.new_open_time,
                new_close_time=mod.new_close_time,
                new_pickup_start_time=mod.new_pickup_start_time,
                new_pickup_end_time=mod.new_pickup_end_time,
                new_is_open_enabled=mod.new_is_open_enabled,
                created_at=mod.created_at
            )
            for mod in modifications
        ]
        
        return StoreOperationReservationResponse(modifications=modification_responses)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"운영 정보 예약 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/operation/reservation", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "예약을 찾을 수 없음"]
    })
)
async def delete_operation_reservation(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    operation_modification_repo: StoreOperationInfoModificationRepositoryDep
):
    """
    운영 정보 변경 예약 삭제
    
    예약된 모든 운영 정보 변경사항을 삭제합니다.
    """
    seller_email = current_user["sub"]
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    try:
        await operation_modification_repo.delete_all_by_store_id(store_id)
        return
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"운영 정보 예약 삭제 중 오류가 발생했습니다: {str(e)}"
        )