from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerDep, CurrentSellerNoActiveDep
from app.domain.seller.service.seller_withdraw import SellerWithdrawService
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.domain.auth.service.jwt import JwtService
from app.domain.auth.service.cookie import clear_auth_cookie, set_auth_cookie
from app.domain.auth.dto.auth import UserType
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/withdraw", tags=["Seller-Withdraw"])


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: ["가게가 오픈 상태에 있어 탈퇴할 수 없음"],
        404: ["판매자를 찾을 수 없음"],
        409: ["이미 판매자 탈퇴 처리 되었음"],
    }),
)
@inject
async def withdraw_seller(
    current_user: CurrentSellerDep,
    store_id: CurrentSellerStoreIdDep,
    withdraw_service: SellerWithdrawService = Depends(
        Provide["seller_withdraw_service"],
    ),
):
    seller_email = current_user["sub"]
    await withdraw_service.request_withdraw(
        seller_email=seller_email, store_id=store_id,
    )

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
        404: ["판매자를 찾을 수 없음", "탈퇴 기록을 찾을 수 없음"],
        409: ["이미 활성화된 계정임"],
    }),
)
@inject
async def cancel_withdraw(
    current_user: CurrentSellerNoActiveDep,
    withdraw_service: SellerWithdrawService = Depends(
        Provide["seller_withdraw_service"],
    ),
    jwt_service: JwtService = Depends(Provide["jwt_service"]),
):
    seller_email = current_user["sub"]
    await withdraw_service.cancel_withdraw(seller_email)

    new_token = jwt_service.create_user_token(
        email=seller_email, user_type=UserType.SELLER.value, is_active=True,
    )
    response = JSONResponse(
        content={"message": "탈퇴가 취소되었습니다"}, status_code=200,
    )
    set_auth_cookie(response, new_token)
    return response
