from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentSellerDep, AsyncSessionDep
from repositories.store import StoreRepository
from repositories.store_product_info import StoreProductInfoRepository
from schemas.store import (
    StoreCreateRequest,
    StoreUpdateRequest,
    StoreResponse,
    StoreProductsResponse,
    StoreProductResponse
)
from utils.id_generator import generate_store_id

router = APIRouter(prefix="/stores", tags=["Seller-Store"])


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_product_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
ProductRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_product_repository)]


@router.get("", response_model=StoreResponse)
async def get_my_stores(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    내 가게 목록 조회
    """
    
    stores = await store_repo.get_by_seller_email(current_user["sub"])
    
    if stores:
        return StoreResponse.model_validate(stores[0])
    
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 가게가 없습니다."
        )


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    request: StoreCreateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    내 가게 등록
    """
    
    store_data = {
        "store_id": generate_store_id(),
        "store_name": request.store_name,
        "seller_email": current_user["sub"]
    }
    
    store = await store_repo.create(**store_data)
    
    return StoreResponse.model_validate(store)


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: str,
    request: StoreUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    내 가게 정보 수정
    """
    
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 가게를 수정할 권한이 없습니다"
        )
    
    update_data = {"store_name": request.store_name}
    updated_store = await store_repo.update(store_id, **update_data)
    
    return StoreResponse.model_validate(updated_store)


@router.get("/{store_id}/products", response_model=StoreProductsResponse)
async def get_store_products(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    내 가게의 상품 목록 조회
    """
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 가게의 상품을 조회할 권한이 없습니다"
        )
    
    products = await product_repo.get_by_store_id(store_id)
    
    return StoreProductsResponse(
        store_id=store.store_id,
        store_name=store.store_name,
        products=[StoreProductResponse.model_validate(product) for product in products],
        total=len(products)
    )
    

@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    내 가게 삭제 - 정책에 따라 구현, 기본 정보를 삭제할 것인가, 아닌가
    """
    
    pass