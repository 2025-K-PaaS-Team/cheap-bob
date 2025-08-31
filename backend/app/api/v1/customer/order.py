from fastapi import APIRouter, HTTPException

from api.deps import CurrentCustomerDep

router = APIRouter(prefix="/orders", tags=["Customer-Order"])


@router.get("")
async def get_order_history(current_user: CurrentCustomerDep):
    """
    주문 내역 조회
    """

    pass


@router.get("/current")
async def get_current_orders(current_user: CurrentCustomerDep):
    """
    현재 진행중인 주문 조회
    """
    
    pass


@router.get("/{order_id}")
async def get_order_detail(order_id: str, current_user: CurrentCustomerDep):
    """
    주문 상세 정보 조회
    """
    
    pass
    
@router.delete("/{order_id}")
async def delete_order(order_id: str, current_user: CurrentCustomerDep):
    """
    주문 취소
    """
    
    pass