from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep, CurrentSellerNoActiveDep
from api.deps.repository import (
    SellerRepositoryDep,
    StoreRepositoryDep,
    StoreOperationInfoRepositoryDep,
    SellerWithdrawReservationRepositoryDep
)
from api.deps.service import JWTServiceDep
from schemas.auth import UserType
from config.settings import settings

router = APIRouter(prefix="/withdraw", tags=["Seller-Withdraw"])

# KST 타임존 설정
KST = timezone(timedelta(hours=9))

@router.post("", status_code=status.HTTP_200_OK,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: ["가게가 오픈 상태에 있어 탈퇴할 수 없음"],
        404: ["판매자를 찾을 수 없음"],
        409: ["이미 판매자 탈퇴 처리 되었음"]
    })
)
async def withdraw_seller(
    current_user: CurrentSellerDep,
    seller_repo: SellerRepositoryDep,
    store_repo: StoreRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep,
    withdraw_repo: SellerWithdrawReservationRepositoryDep
):
    """
    판매자 탈퇴 처리
    
    탈퇴 처리 후 쿠키를 만료시킵니다.
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)

    today = datetime.now(KST).weekday()
    
    operation_data = await operation_repo.get_by_store_and_day(store_id, today)
    
    if operation_data.is_currently_open:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가게 오픈 상태여서 탈퇴할 수 없습니다"
        )
    
    seller = await seller_repo.get_by_pk(seller_email)
    
    if not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 탈퇴 처리 되었습니다."
        )
    
    await seller_repo.update(seller_email, is_active=False)
    
    await withdraw_repo.create_withdrawal(
        seller_email=seller_email,
        withdrawn_at=datetime.now(timezone.utc)
    )
    
    response = JSONResponse(
        content={"message": "탈퇴가 완료되었습니다"},
        status_code=200
    )
    
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=0,
        path="/"
    )
    
    return response


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
    withdraw_repo: SellerWithdrawReservationRepositoryDep,
    jwt_service: JWTServiceDep
):
    """
    판매자 탈퇴 취소
    
    탈퇴한 계정을 다시 활성화하고 새로운 토큰을 쿠키로 발급합니다.
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
    
    withdraw_record = await withdraw_repo.get_by_seller_email(seller_email)
    
    if not withdraw_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="탈퇴 기록을 찾을 수 없습니다"
        )
    
    await seller_repo.update(seller.email, is_active=True)
    
    await withdraw_repo.delete_by_seller_email(seller_email)
    
    new_token = jwt_service.create_user_token(
        email=seller_email,
        user_type=UserType.SELLER.value,
        is_active=True
    )
    
    response = JSONResponse(
        content={"message": "탈퇴가 취소되었습니다"},
        status_code=200
    )
    
    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.COOKIE_EXPIRE_MINUTES,
        path="/"
    )
    
    return response