from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerDep, CurrentSellerNoActiveDep
from app.domain.seller.service.seller_withdraw import SellerWithdrawService
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.exception import (
    SellerAlreadyActiveError,
    SellerAlreadyWithdrawnError,
    SellerNotFoundError,
    SellerStoreOpenError,
    SellerWithdrawalRecordNotFoundError,
    StoreNotFoundError,
)
from app.domain.auth.service.jwt import JwtService
from app.domain.auth.dto.auth import UserType
from app.core.openapi import create_error_responses
from app.config.setting import settings


router = APIRouter(prefix="/withdraw", tags=["Seller-Withdraw"])


def _samesite(state: str | None) -> str:
    return "none" if (state == "1004" and settings.ENVIRONMENT == "dev") else "lax"


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
    state: str | None = Query(None, description="로컬 테스트 분기용"),
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    withdraw_service: SellerWithdrawService = Depends(
        Provide["seller_withdraw_service"],
    ),
):
    seller_email = current_user["sub"]
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(seller_email)
        await withdraw_service.request_withdraw(
            seller_email=seller_email, store_id=store_id,
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SellerStoreOpenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except SellerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SellerAlreadyWithdrawnError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    response = JSONResponse(
        content={"message": "탈퇴가 완료되었습니다"}, status_code=200,
    )
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True,
        samesite=_samesite(state),
        max_age=0,
        path="/",
    )
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
    state: str | None = Query(None, description="로컬 테스트 분기용"),
    withdraw_service: SellerWithdrawService = Depends(
        Provide["seller_withdraw_service"],
    ),
    jwt_service: JwtService = Depends(Provide["jwt_service"]),
):
    seller_email = current_user["sub"]
    try:
        await withdraw_service.cancel_withdraw(seller_email)
    except SellerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SellerWithdrawalRecordNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SellerAlreadyActiveError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    new_token = jwt_service.create_user_token(
        email=seller_email, user_type=UserType.SELLER.value, is_active=True,
    )
    response = JSONResponse(
        content={"message": "탈퇴가 취소되었습니다"}, status_code=200,
    )
    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        secure=True,
        samesite=_samesite(state),
        max_age=settings.COOKIE_EXPIRE_MINUTES,
        path="/",
    )
    return response
