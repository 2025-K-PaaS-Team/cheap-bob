from api.deps.repository import (
    CustomerDetailRepositoryDep,
    StoreRepositoryDep,
    StoreProductInfoRepositoryDep
)


async def get_customer_status(
    customer_email: str,
    customer_detail_repo: CustomerDetailRepositoryDep
) -> str:
    """Customer의 등록 상태를 확인"""
    customer_detail = await customer_detail_repo.get_by_customer(customer_email)
    
    if customer_detail is None:
        return "profile"
    else:
        return "complete"


async def get_seller_status(
    seller_email: str,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
) -> str:
    """Seller의 등록 상태를 확인"""
    existing_stores = await store_repo.get_by_seller_email(seller_email)
    
    if not existing_stores:
        return "store"
    else:
        store = existing_stores[0]
        product_count = await product_repo.count_products_by_store(store.store_id)
        
        if product_count == 0:
            return "product"
        else:
            return "complete"