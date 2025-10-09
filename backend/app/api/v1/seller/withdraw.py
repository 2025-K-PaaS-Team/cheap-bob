from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep, CurrentSellerNoActiveDep
from api.deps.repository import (
    SellerRepositoryDep,
    StoreRepositoryDep,
    StoreOperationInfoRepositoryDep
)
from api.deps.service import JWTServiceDep
from schemas.auth import UserType
from schemas.withdraw import WithdrawResponse

from database.mongodb_models import SellerWithdrawReservation

router = APIRouter(prefix="/withdraw", tags=["Seller-Withdraw"])


@router.post("", status_code=status.HTTP_200_OK,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: ["진행 중인 주문이 있어 탈퇴할 수 없음"],
        404: ["판매자를 찾을 수 없음"],
        409: ["이미 판매자 탈퇴 처리 되었음"]
    })
)
async def withdraw_seller(
    current_user: CurrentSellerDep,
    seller_repo: SellerRepositoryDep,
    store_repo: StoreRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep,
    jwt_service: JWTServiceDep
):
    """
    판매자 탈퇴 처리
    
    탈퇴 처리 후 새 토큰을 발급합니다.
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    if await store_repo.has_active_orders(store_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="진행 중인 주문이 있어 탈퇴할 수 없습니다"
        )
        
    await operation_repo.update_where(
        filters={"store_id": store_id},
        is_currently_open=False
    )
    
    seller = await seller_repo.get_by_pk(seller_email)
    
    if not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 탈퇴 처리 되었습니다."
        )
    
    await seller_repo.update(seller_email, is_active=False)
    
    withdraw_reservation = SellerWithdrawReservation(
        seller_email=seller_email,
        withdrawn_at=datetime.now(timezone.utc)
    )
    await withdraw_reservation.insert()
    
    new_token = jwt_service.create_user_token(
        email=seller_email,
        user_type=UserType.SELLER.value,
        is_active=False
    )
    
    return WithdrawResponse(message="탈퇴가 완료되었습니다", access_token=new_token)


@router.delete("/cancel", status_code=status.HTTP_200_OK,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["판매자를 찾을 수 없음", "탈퇴 기록을 찾을 수 없음"],
        409: ["이미 활성화된 계정임"]
    })
)
async def cancel_withdraw(
    current_user: CurrentSellerNoActiveDep,
    seller_repo: SellerRepositoryDep,
    jwt_service: JWTServiceDep
):
    """
    판매자 탈퇴 취소
    
    탈퇴한 계정을 다시 활성화하고 새로운 토큰을 발급합니다.
    """
    seller_email = current_user["sub"]
    
    seller = await seller_repo.get_by_email(seller_email)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="판매자를 찾을 수 없습니다"
        )
    
    if seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 활성화된 계정입니다"
        )
    
    withdraw_record = await SellerWithdrawReservation.find_one(
        SellerWithdrawReservation.seller_email == seller_email
    )
    
    if not withdraw_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="탈퇴 기록을 찾을 수 없습니다"
        )
    
    await seller_repo.update(seller.email, is_active=True)
    
    await withdraw_record.delete()
    
    new_token = jwt_service.create_user_token(
        email=seller_email,
        user_type=UserType.SELLER.value,
        is_active=True
    )
    return WithdrawResponse(message="탈퇴가 취소되었습니다", access_token=new_token)