from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    SellerRepositoryDep,
    StoreRepositoryDep,
    StoreOperationInfoRepositoryDep
)

from database.mongodb_models import SellerWithdrawReservation

router = APIRouter(prefix="/withdraw", tags=["Seller-Withdraw"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: ["진행 중인 주문이 있어 탈퇴할 수 없음"],
        404: ["판매자를 찾을 수 없음"]
    })
)
async def withdraw_seller(
    current_user: CurrentSellerDep,
    seller_repo: SellerRepositoryDep,
    store_repo: StoreRepositoryDep,
    operation_repo: StoreOperationInfoRepositoryDep
):
    """
    판매자 탈퇴 처리
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
    
    await seller_repo.update(seller_email, is_active=False)
    
    withdraw_reservation = SellerWithdrawReservation(
        seller_email=seller_email,
        withdrawn_at=datetime.now(timezone.utc)
    )
    await withdraw_reservation.insert()