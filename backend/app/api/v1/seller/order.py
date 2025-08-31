from fastapi import APIRouter, HTTPException

from api.deps import CurrentSellerDep

router = APIRouter(prefix="/orders", tags=["Seller-Order"])


@router.get("")
async def get_store_orders(current_user: CurrentSellerDep):
    """
    가게의 주문 목록 조회
    """
    
    pass


@router.get("/pending")
async def get_pending_orders(current_user: CurrentSellerDep):
    """
    처리 대기중인 주문 조회
    """
    
    pass


@router.patch("/{order_id}/accept")
async def update_order_accept(order_id: str, current_user: CurrentSellerDep):
    """
    주문 수락
    """
    
    pass


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, current_user: CurrentSellerDep):
    """
    주문 취소
    """
    
    pass