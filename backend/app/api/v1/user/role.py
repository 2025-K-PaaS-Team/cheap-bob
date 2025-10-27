from fastapi import APIRouter

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentUserNoActiveDep
from api.deps.repository import (
    CustomerDetailRepositoryDep,
    StoreRepositoryDep,
    StoreProductInfoRepositoryDep
)
from schemas.user import UserRoleResponse
from utils.user_utils import get_customer_status, get_seller_status

router = APIRouter(prefix="/role", tags=["User-Role"])


@router.get(
    "",
    response_model=UserRoleResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_user_role(
    current_user: CurrentUserNoActiveDep,
    customer_detail_repo: CustomerDetailRepositoryDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
):
    """현재 사용자의 역할 정보와 등록 상태를 조회합니다."""
    email = current_user["sub"]
    user_type = current_user["user_type"]
    
    if user_type == "customer":
        status = await get_customer_status(email, customer_detail_repo)
    else:
        status = await get_seller_status(email, store_repo, product_repo)
    
    return UserRoleResponse(
        email=email,
        user_type=user_type,
        is_active=current_user.get("is_active", True),
        status=status
    )