from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status

from utils.docs_error import create_error_responses

from api.deps import CurrentSellerDep, AsyncSessionDep
from repositories.store import StoreRepository
from repositories.store_product_info import StoreProductInfoRepository, StockUpdateResult
from schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductStockUpdateRequest,
    ProductResponse
)
from utils.id_generator import generate_product_id
from config.settings import settings

router = APIRouter(prefix="/products", tags=["Seller-Product"])


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_product_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
ProductRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_product_repository)]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })  
)
async def create_product(
    request: ProductCreateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    새 상품 등록
    """
    
    # 가게 소유권 확인
    store = await store_repo.get_by_store_id(request.store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 가게에 상품을 등록할 권한이 없습니다"
        )
    
    # 상품 데이터 생성
    product_data = {
        "product_id": generate_product_id(),
        "store_id": request.store_id,
        "product_name": request.product_name,
        "initial_stock": request.initial_stock,
        "current_stock": request.initial_stock,  # 초기에는 동일
        "price": request.price,
        "sale": request.sale,
        "version": 1
    }
    
    product = await product_repo.create(**product_data)
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })              
)
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    상품 정보 수정
    """
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 가게 소유권 확인
    store = await store_repo.get_by_store_id(product.store_id)
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 상품을 수정할 권한이 없습니다"
        )
    
    # 업데이트할 데이터만 추출
    update_data = request.model_dump(exclude_unset=True)
    
    if update_data:
        updated_product = await product_repo.update(product_id, **update_data)
        return ProductResponse.model_validate(updated_product)
    
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}/stock/up", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "이 상품의 재고를 수정할 권한이 없음",
        404: "상품을 찾을 수 없음",
        409: "재고 업데이트 중 충돌이 발생"
    })
)
async def increase_product_stock(
    product_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    상품 재고 1개 증가
    """
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 가게 소유권 확인
    store = await store_repo.get_by_store_id(product.store_id)
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 상품의 재고를 수정할 권한이 없습니다"
        )
    
    # 재고 증가 (낙관적 락 사용, 최대 재시도 횟수까지)
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        result = await product_repo.restore_stock(product_id, 1)
        
        if result == StockUpdateResult.SUCCESS:
            # 업데이트된 상품 조회
            updated_product = await product_repo.get_by_product_id(product_id)
            return ProductResponse.model_validate(updated_product)
        
        if attempt == max_retries - 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="재고 업데이트 중 충돌이 발생했습니다. 다시 시도해주세요."
            )


@router.patch("/{product_id}/stock/down", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "이 상품의 재고를 수정할 권한이 없음",
        404: "상품을 찾을 수 없음",
        409: ["남은 재고가 없음", "재고 업데이트 중 충돌이 발생"]
    })
)
async def decrease_product_stock(
    product_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    상품 재고 1개 감소
    """
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 가게 소유권 확인
    store = await store_repo.get_by_store_id(product.store_id)
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 상품의 재고를 수정할 권한이 없습니다"
        )
    
    # 재고 감소 (낙관적 락 사용, 최대 재시도 횟수까지)
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        result = await product_repo.decrease_stock(product_id, 1)
        
        if result == StockUpdateResult.SUCCESS:
            # 업데이트된 상품 조회
            updated_product = await product_repo.get_by_product_id(product_id)
            return ProductResponse.model_validate(updated_product)
        elif result == StockUpdateResult.INSUFFICIENT_STOCK:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="남은 재고가 없습니다."
            )
        
        if attempt == max_retries - 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="재고 업데이트 중 충돌이 발생했습니다. 다시 시도해주세요."
            )



@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: ProductRepositoryDep
):
    """
    상품 삭제(미구현) - 논의 필요
    """
    
    pass

    # # 상품 조회
    # product = await product_repo.get_by_product_id(product_id)
    
    # if not product:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="상품을 찾을 수 없습니다"
    #     )
    
    # # 가게 소유권 확인
    # store = await store_repo.get_by_store_id(product.store_id)
    
    # if store.seller_email != current_user["sub"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="이 상품을 삭제할 권한이 없습니다"
    #     )
    
    # await product_repo.delete(product_id)