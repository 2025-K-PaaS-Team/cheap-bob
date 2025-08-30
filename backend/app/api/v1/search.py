from fastapi import APIRouter, HTTPException, Path

from schemas.product import (
    ProductsResponse, ProductInfo
)

from examples.products import fake_stores_products

router = APIRouter(prefix="/search", tags=["search"])





@router.get("/stores/{store_id}/products", response_model=ProductsResponse)
async def get_store_products(store_id: str = Path(..., description="가게 고유 ID")):
    """
    가게 상품 조회 API
    """
    if store_id not in fake_stores_products:
        raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
    
    store_data = fake_stores_products[store_id]
    
    return ProductsResponse(
        store_id=store_id,
        store_name=store_data["store_name"],
        products=[ProductInfo(**product) for product in store_data["products"]]
        
    )