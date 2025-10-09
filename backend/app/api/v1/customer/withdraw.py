from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentCustomerDep, CurrentCustomerNoActiveDep
from api.deps.repository import (
    CustomerRepositoryDep,
    OrderCurrentItemRepositoryDep,
    CustomerWithdrawReservationRepositoryDep
)
from api.deps.service import JWTServiceDep
from schemas.auth import UserType
from schemas.withdraw import WithdrawResponse

router = APIRouter(prefix="/withdraw", tags=["Customer-Withdraw"])


@router.post("", status_code=status.HTTP_200_OK, response_model=WithdrawResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: ["진행 중인 주문이 있어 탈퇴할 수 없음"],
        404: ["소비자를 찾을 수 없음"],
        409: ["이미 소비자 탈퇴 처리 되었음"]
    })
)
async def withdraw_customer(
    current_user: CurrentCustomerDep,
    customer_repo: CustomerRepositoryDep,
    order_repo: OrderCurrentItemRepositoryDep,
    withdraw_repo: CustomerWithdrawReservationRepositoryDep,
    jwt_service: JWTServiceDep
):
    """
    소비자 탈퇴 처리
    
    탈퇴 처리 후 새 토큰을 발급합니다.
    """
    customer_email = current_user["sub"]
    
    # 소비자 확인
    customer = await customer_repo.get_by_email(customer_email)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소비자를 찾을 수 없습니다"
        )
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 탈퇴 처리 되었습니다."
        )
    
    active_orders = await order_repo.get_customer_active_orders(customer_email)
    if active_orders:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="진행 중인 주문이 있어 탈퇴할 수 없습니다"
        )
    
    await customer_repo.update(customer_email, is_active=False)
    
    await withdraw_repo.create_withdrawal(
        customer_email=customer_email,
        withdrawn_at=datetime.now(timezone.utc)
    )
    
    new_token = jwt_service.create_user_token(
        email=customer_email,
        user_type=UserType.CUSTOMER.value,
        is_active=False
    )
    
    return WithdrawResponse(message="탈퇴가 완료되었습니다", access_token=new_token)


@router.delete("/cancel", status_code=status.HTTP_200_OK, response_model=WithdrawResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["소비자를 찾을 수 없음", "탈퇴 기록을 찾을 수 없음"],
        409: ["이미 활성화된 계정임"]
    })
)
async def cancel_withdraw(
    current_user: CurrentCustomerNoActiveDep,
    customer_repo: CustomerRepositoryDep,
    withdraw_repo: CustomerWithdrawReservationRepositoryDep,
    jwt_service: JWTServiceDep
):
    """
    소비자 탈퇴 취소
    
    탈퇴한 계정을 다시 활성화하고 새로운 토큰을 발급합니다.
    """
    customer_email = current_user["sub"]
    
    customer = await customer_repo.get_by_email(customer_email)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소비자를 찾을 수 없습니다"
        )
    
    if customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 활성화된 계정입니다"
        )
    
    withdraw_record = await withdraw_repo.get_by_customer_email(customer_email)
    
    if not withdraw_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="탈퇴 기록을 찾을 수 없습니다"
        )
    
    await customer_repo.update(customer.email, is_active=True)
    
    await withdraw_repo.delete_by_customer_email(customer_email)
    
    new_token = jwt_service.create_user_token(
        email=customer_email,
        user_type=UserType.CUSTOMER.value,
        is_active=True
    )
    
    return WithdrawResponse(message="탈퇴가 취소되었습니다", access_token=new_token)