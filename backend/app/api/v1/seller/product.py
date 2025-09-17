from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses

from api.deps.auth import CurrentSellerDep
from api.deps.repository import (
    StoreRepositoryDep,
    StoreProductInfoRepositoryDep,
    ProductNutritionRepositoryDep
)
from repositories.store_product_info import StockUpdateResult
from schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    StoreProductsResponse,
    ProductNutritionRequest
)
from utils.id_generator import generate_product_id
from config.settings import settings

router = APIRouter(prefix="/products", tags=["Seller-Product"])


@router.post("/register", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
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
    product_repo: StoreProductInfoRepositoryDep,
    nutrition_repo: ProductNutritionRepositoryDep
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
        "description": request.description,
        "initial_stock": request.initial_stock,
        "current_stock": request.initial_stock,  # 초기에는 동일
        "price": request.price,
        "sale": request.sale,
        "version": 1
    }
    
    product = await product_repo.create(**product_data)
    
    # 영양 정보 추가
    if request.nutrition_types:
        await nutrition_repo.add_multiple_nutrition_to_product(
            product_id=product.product_id,
            nutrition_types=request.nutrition_types
        )
    
    # 영양 타입 목록 조회
    nutrition_types = await nutrition_repo.get_nutrition_types_by_product(product.product_id)
    
    # 응답 생성
    response_data = {
        **product.__dict__,
        "nutrition_types": nutrition_types
    }
    
    return ProductResponse.model_validate(response_data)


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
    product_repo: StoreProductInfoRepositoryDep,
    nutrition_repo: ProductNutritionRepositoryDep
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
    else:
        updated_product = product
    
    # 영양 타입 목록 조회
    nutrition_types = await nutrition_repo.get_nutrition_types_by_product(product_id)
    
    # 응답 생성
    response_data = {
        **updated_product.__dict__,
        "nutrition_types": nutrition_types
    }
    
    return ProductResponse.model_validate(response_data)


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
    product_repo: StoreProductInfoRepositoryDep,
    nutrition_repo: ProductNutritionRepositoryDep
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
            
            # 영양 타입 목록 조회
            nutrition_types = await nutrition_repo.get_nutrition_types_by_product(product_id)
            
            # 응답 생성
            response_data = {
                **updated_product.__dict__,
                "nutrition_types": nutrition_types
            }
            
            return ProductResponse.model_validate(response_data)
        
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
    product_repo: StoreProductInfoRepositoryDep,
    nutrition_repo: ProductNutritionRepositoryDep
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
            
            # 영양 타입 목록 조회
            nutrition_types = await nutrition_repo.get_nutrition_types_by_product(product_id)
            
            # 응답 생성
            response_data = {
                **updated_product.__dict__,
                "nutrition_types": nutrition_types
            }
            
            return ProductResponse.model_validate(response_data)
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




@router.get("/store/{store_id}", response_model=StoreProductsResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게를 조회할 권한이 없음",
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_products(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    nutrition_repo: ProductNutritionRepositoryDep
):
    """
    특정 가게의 모든 상품 목록 조회
    """
    # 가게 확인 및 소유권 검사
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
    
    # 가게의 모든 상품 조회
    products = await product_repo.get_by_store_id(store_id)
    
    if not products:
        return StoreProductsResponse(
            store_id=store.store_id,
            store_name=store.store_name,
            products=[]
        )
    
    # 모든 상품 ID 추출
    product_ids = [product.product_id for product in products]
    
    # 모든 상품의 영양 정보를 한 번에 조회
    nutrition_by_product = await nutrition_repo.get_nutrition_types_by_products(product_ids)
    
    # 각 상품에 대한 응답 생성
    product_responses = []
    for product in products:
        nutrition_types = nutrition_by_product.get(product.product_id, [])
        
        response_data = {
            **product.__dict__,
            "nutrition_types": nutrition_types
        }
        product_responses.append(ProductResponse.model_validate(response_data))
    
    return StoreProductsResponse(
        store_id=store.store_id,
        store_name=store.store_name,
        products=product_responses
    )


@router.post("/{product_id}/nutrition", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "이 상품의 영양 정보를 수정할 권한이 없음",
        404: "상품을 찾을 수 없음",
        400: "이미 존재하는 영양 타입이 있음"
    })
)
async def add_product_nutrition(
    product_id: str,
    request: ProductNutritionRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    nutrition_repo: ProductNutritionRepositoryDep
):
    """
    상품에 영양 정보 추가
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
            detail="이 상품의 영양 정보를 수정할 권한이 없습니다"
        )
    
    # 기존 영양 정보 조회
    existing_nutrition = await nutrition_repo.get_nutrition_types_by_product(product_id)
    
    # 중복 체크
    duplicates = [nt for nt in request.nutrition_types if nt in existing_nutrition]
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 존재하는 영양 타입: {', '.join([d.value for d in duplicates])}"
        )
    
    # 영양 정보 추가
    await nutrition_repo.add_multiple_nutrition_to_product(
        product_id=product_id,
        nutrition_types=request.nutrition_types
    )
    
    # 업데이트된 영양 정보 조회
    updated_nutrition = await nutrition_repo.get_nutrition_types_by_product(product_id)
    
    # 응답 생성
    response_data = {
        **product.__dict__,
        "nutrition_types": updated_nutrition
    }
    
    return ProductResponse.model_validate(response_data)


@router.delete("/{product_id}/nutrition", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "이 상품의 영양 정보를 수정할 권한이 없음",
        404: ["상품을 찾을 수 없음", "삭제할 영양 정보를 찾을 수 없음"]
    })
)
async def remove_product_nutrition(
    product_id: str,
    request: ProductNutritionRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    nutrition_repo: ProductNutritionRepositoryDep
):
    """
    상품에서 영양 정보 삭제
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
            detail="이 상품의 영양 정보를 수정할 권한이 없습니다"
        )
    
    # 각 영양 타입 삭제
    not_found = []
    for nutrition_type in request.nutrition_types:
        removed = await nutrition_repo.remove_nutrition_from_product(
            product_id=product_id,
            nutrition_type=nutrition_type
        )
        if not removed:
            not_found.append(nutrition_type)
    
    if not_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"존재하지 않는 영양 타입: {', '.join([nt.value for nt in not_found])}"
        )
    
    # 업데이트된 영양 정보 조회
    updated_nutrition = await nutrition_repo.get_nutrition_types_by_product(product_id)
    
    # 응답 생성
    response_data = {
        **product.__dict__,
        "nutrition_types": updated_nutrition
    }
    
    return ProductResponse.model_validate(response_data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
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