from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Path, Depends, status

from api.deps import CurrentCustomerDep, AsyncSessionDep
from schemas.product import ProductsResponse, ProductInfo
from schemas.store import StoreResponse
from repositories.store import StoreRepository
from repositories.store_product_info import StoreProductInfoRepository

router = APIRouter(prefix="/search", tags=["Customer-Search"])


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_product_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
ProductRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_product_repository)]


@router.get("/stores", response_model=List[StoreResponse])
async def get_stores(
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep
):
    """
    가게 조회 API
    """
    
    stores = await store_repo.get_many(order_by=["-created_at"])
    
    if not stores:
        return []
    
    return [StoreResponse.model_validate(store) for store in stores]


@router.get("/stores/{store_id}/products", response_model=ProductsResponse)
async def get_store_products(
    store_id: str,
    current_user: CurrentCustomerDep,
    store_repo: StoreRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    가게 상품 조회 API
    """
    
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    products = await product_repo.get_by_store_id(store_id)
    
    product_list = [
        ProductInfo(
            product_id=product.product_id,
            product_name=product.product_name,
            stock=product.current_stock,
            price=product.price
        ) for product in products
    ]
    
    return ProductsResponse(
        store_id=store.store_id,
        store_name=store.store_name,
        products=product_list
    )