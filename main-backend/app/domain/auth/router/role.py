from fastapi import APIRouter, Depends, HTTPException, Request, status
from dependency_injector.wiring import Provide, inject

from app.domain.auth.service.registration_status import RegistrationStatusService
from app.domain.auth.schema.role import UserRoleResponse
from app.domain.auth.dto.auth import UserType


router = APIRouter(prefix="/role")


@router.get("", response_model=UserRoleResponse)
@inject
async def get_user_role(
    request: Request,
    registration_status_service: RegistrationStatusService = Depends(
        Provide["registration_status_service"],
    ),
):
    """현재 사용자의 역할 정보와 등록 단계를 조회한다."""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    email = user["sub"]
    user_type_str = user["user_type"]
    user_type = UserType(user_type_str)

    registration_status = await registration_status_service.get_status(
        email=email,
        user_type=user_type,
    )

    return UserRoleResponse(
        email=email,
        user_type=user_type_str,
        is_active=user.get("is_active", True),
        status=registration_status,
    )
