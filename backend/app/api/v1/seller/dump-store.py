from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status

from utils.docs_error import create_error_responses

from api.deps import CurrentSellerDep, AsyncSessionDep
from repositories.store import StoreRepository
from repositories.store_product_info import StoreProductInfoRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from schemas.store import (
    StoreUpdateRequest,
    StoreResponse,
    StoreProductsResponse,
    StoreProductResponse,
    StorePaymentInfoCreateRequest,
    StorePaymentInfoResponse,
    StorePaymentInfoStatusResponse
)

router = APIRouter(prefix="/stores", tags=["Seller-Store"])


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_product_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


def get_payment_repository(session: AsyncSessionDep) -> StorePaymentInfoRepository:
    return StorePaymentInfoRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
ProductRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_product_repository)]
PaymentRepositoryDep = Annotated[StorePaymentInfoRepository, Depends(get_payment_repository)]


@router.get("", response_model=StoreResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게가 없음"
    }) 
)
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


@router.put("/{store_id}", response_model=StoreResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })            
)
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


@router.get("/{store_id}/products", response_model=StoreProductsResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })  
)
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
    내 가게 삭제(미구현) - 정책에 따라 구현, 기본 정보를 삭제할 것인가, 아닌가
    """
    
    pass


@router.get("/{store_id}/payment-info/status", response_model=StorePaymentInfoStatusResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })  
)
async def check_payment_info_status(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    payment_repo: PaymentRepositoryDep
):
    """
    가게의 결제 정보 등록 상태 확인
    """
    
    # 가게 존재 여부 및 권한 확인
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 가게의 결제 정보를 조회할 권한이 없습니다"
        )
    
 
    info_status = await payment_repo.has_complete_info(store_id)
    
    return StorePaymentInfoStatusResponse(
        info_status=info_status
    )


@router.post("/{store_id}/payment-info", response_model=StorePaymentInfoResponse, status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        403: "가게를 수정할 수 있는 권한이 없음",
        404:"등록된 가게를 찾을 수 없음"
    })  
)
async def register_payment_info(
    store_id: str,
    request: StorePaymentInfoCreateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    payment_repo: PaymentRepositoryDep
):
    """
    가게의 결제 정보 등록
    """
    
    # 가게 존재 여부 및 권한 확인
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다"
        )
    
    if store.seller_email != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 가게의 결제 정보를 등록할 권한이 없습니다"
        )
    
    # 이미 결제 정보가 있는지 확인
    existing_payment_info = await payment_repo.get_by_store_id(store_id)
    
    if existing_payment_info:
        # 이미 있으면 업데이트
        payment_info = await payment_repo.update_portone_info(
            store_id=store_id,
            portone_store_id=request.portone_store_id,
            portone_channel_id=request.portone_channel_id,
            portone_secret_key=request.portone_secret_key
        )
    else:
        # 없으면 새로 생성
        payment_data = {
            "store_id": store_id,
            "portone_store_id": request.portone_store_id,
            "portone_channel_id": request.portone_channel_id,
            "portone_secret_key": request.portone_secret_key
        }
        payment_info = await payment_repo.create(**payment_data)
    
    return StorePaymentInfoResponse(
        store_id=payment_info.store_id,
        portone_store_id=payment_info.portone_store_id,
        portone_channel_id=payment_info.portone_channel_id
    )