from fastapi import APIRouter, HTTPException

from api.deps import CurrentSellerDep

router = APIRouter(prefix="/stores", tags=["Seller-Store"])


@router.get("")
async def get_my_stores(current_user: CurrentSellerDep):
    """
    내 가게 목록 조회
    """
    
    pass


@router.post("")
async def create_store(current_user: CurrentSellerDep):
    """
    내 가게 등록
    """
    pass


@router.put("/{store_id}")
async def update_store(store_id: str, current_user: CurrentSellerDep):
    """
    내 가게 정보 수정
    """
    
    pass


@router.delete("/{store_id}")
async def delete_store(store_id: str, current_user: CurrentSellerDep):
    """
    내 가게 삭제
    """
    
    pass


@router.get("/{store_id}/products")
async def get_store_products(store_id: str, current_user: CurrentSellerDep):
    """
    내 가게의 상품 목록 조회
    """
    
    pass