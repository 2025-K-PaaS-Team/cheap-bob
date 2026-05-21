from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep, CurrentCustomerNoActiveDep
from app.domain.customer.service.exception import (
    CustomerActiveOrdersExistError,
    CustomerAlreadyActiveError,
    CustomerAlreadyWithdrawnError,
    CustomerNotFoundError,
    WithdrawalRecordNotFoundError,
)
from app.domain.customer.service.customer_withdraw import CustomerWithdrawService
from app.domain.auth.service.jwt import JwtService
from app.domain.auth.dto.auth import UserType
from app.domain.auth.cookie import clear_auth_cookie, set_auth_cookie
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/withdraw", tags=["Customer-Withdraw"])


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: ["진행 중인 주문이 있어 탈퇴할 수 없음"],
        404: ["소비자를 찾을 수 없음"],
        409: ["이미 소비자 탈퇴 처리 되었음"],
    }),
)
@inject
async def withdraw_customer(
    current_user: CurrentCustomerDep,
    withdraw_service: CustomerWithdrawService = Depends(
        Provide["customer_withdraw_service"],
    ),
):
    """소비자 탈퇴 — 30일 유예 reservation 등록 + 쿠키 만료."""
    try:
        await withdraw_service.request_withdraw(current_user["sub"])
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CustomerAlreadyWithdrawnError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except CustomerActiveOrdersExistError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    response = JSONResponse(
        content={"message": "탈퇴가 완료되었습니다"}, status_code=200,
    )
    clear_auth_cookie(response)
    return response


@router.delete(
    "/cancel",
    status_code=status.HTTP_200_OK,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["소비자를 찾을 수 없음", "탈퇴 기록을 찾을 수 없음"],
        409: ["이미 활성화된 계정임"],
    }),
)
@inject
async def cancel_withdraw(
    current_user: CurrentCustomerNoActiveDep,
    withdraw_service: CustomerWithdrawService = Depends(
        Provide["customer_withdraw_service"],
    ),
    jwt_service: JwtService = Depends(Provide["jwt_service"]),
):
    """탈퇴 취소 — 계정 재활성 + 새 access_token 발급."""
    customer_email = current_user["sub"]
    try:
        await withdraw_service.cancel_withdraw(customer_email)
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except WithdrawalRecordNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CustomerAlreadyActiveError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    new_token = jwt_service.create_user_token(
        email=customer_email,
        user_type=UserType.CUSTOMER.value,
        is_active=True,
    )

    response = JSONResponse(
        content={"message": "탈퇴가 취소되었습니다"}, status_code=200,
    )
    set_auth_cookie(response, new_token)
    return response
