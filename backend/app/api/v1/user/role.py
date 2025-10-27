from fastapi import APIRouter

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentUserNoActiveDep
from schemas.user import UserRoleResponse

router = APIRouter(prefix="/role", tags=["User-Role"])


@router.get(
    "",
    response_model=UserRoleResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_user_role(
    current_user: CurrentUserNoActiveDep
):
    """현재 사용자의 역할 정보를 조회합니다."""
    return UserRoleResponse(
        email=current_user["sub"],
        user_type=current_user["user_type"],
        is_active=current_user.get("is_active", True)
    )