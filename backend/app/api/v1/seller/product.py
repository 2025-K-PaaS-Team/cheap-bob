from fastapi import APIRouter, HTTPException

from api.deps import CurrentSellerDep

router = APIRouter(prefix="/products", tags=["Seller-Product"])


@router.post("")
async def create_product(current_user: CurrentSellerDep):
    """
    새 상품 등록
    """
    
    pass


@router.put("/{product_id}")
async def update_product(product_id: str, current_user: CurrentSellerDep):
    """
    상품 정보 수정
    """
    
    pass


@router.delete("/{product_id}")
async def delete_product(product_id: str, current_user: CurrentSellerDep):
    """
    상품 삭제
    """
    
    pass


@router.patch("/{product_id}/stock")
async def update_product_stock(product_id: str, current_user: CurrentSellerDep):
    """
    상품 재고 업데이트
    """
    
    pass