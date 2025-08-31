from fastapi import APIRouter, HTTPException, Path

from api.deps import CurrentCustomerDep, CurrentUserOptionalDep
from schemas.product import ProductsResponse, ProductInfo
from examples.products import fake_stores_products

router = APIRouter(prefix="/search", tags=["Customer-Search"])


@router.get("/stores")
async def get_store_products(
    current_user: CurrentCustomerDep
):
    """
    가게 조회 API
    """
    
    pass


@router.get("/stores/{store_id}/products", response_model=ProductsResponse)
async def get_store_products(
    current_user: CurrentCustomerDep,
    store_id: str = Path(..., description="가게 고유 ID")
):
    """
    가게 상품 조회 API
    """
    
    pass