from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
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
    ProductNutritionRequest
)
from utils.id_generator import generate_product_id
from config.settings import settings

router = APIRouter(prefix="/store/products", tags=["Seller-Product"])


@router.post("/register", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"등록된 가게를 찾을 수 없음"
    })  
)
async def create_product(
    request: ProductCreateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
):
    """
    새 상품 등록
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    product_id = generate_product_id()
    
    product, nutrition_types = await product_repo.create_product_with_nutrition(
        product_id=product_id,
        store_id=store_id,
        product_name=request.product_name,
        description=request.description,
        initial_stock=request.initial_stock,
        price=request.price,
        sale=request.sale,
        nutrition_types=request.nutrition_types
    )

    response_data = {
        **product.__dict__,
        "current_stock": product.current_stock,
        "nutrition_types": nutrition_types
    }
    
    return ProductResponse.model_validate(response_data)


@router.get("/{product_id}", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음"
    })
)
async def get_product(
    product_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep
):
    """
    상품 상세 정보 조회
    """
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    product = await product_repo.get_with_nutrition_info(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 상품이 현재 판매자의 가게에 속하는지 확인
    if product.store_id != store_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    nutrition_types = [n.nutrition_type for n in product.nutrition_info] if product.nutrition_info else []
    
    response_data = {
        **product.__dict__,
        "current_stock": product.current_stock,
        "nutrition_types": nutrition_types
    }
    
    return ProductResponse.model_validate(response_data)


@router.put("/{product_id}", response_model=ProductResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
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
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 업데이트할 데이터만 추출
    update_data = request.model_dump(exclude_unset=True)
    
    # sale이 0이면 None으로 변경
    if 'sale' in update_data and update_data['sale'] == 0:
        update_data['sale'] = None
    
    if update_data:
        await product_repo.update(product_id, **update_data)

    updated_product = await product_repo.get_with_nutrition_info(product_id)

    nutrition_types = [n.nutrition_type for n in updated_product.nutrition_info] if updated_product.nutrition_info else []
    
    # 응답 생성
    response_data = {
        **updated_product.__dict__,
        "current_stock": updated_product.current_stock,
        "nutrition_types": nutrition_types
    }
    
    return ProductResponse.model_validate(response_data)


@router.patch("/{product_id}/stock/up", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
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
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 재고 증가
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        result = await product_repo.adjust_admin_stock(product_id, 1)  # 1개 증가
        
        if result == StockUpdateResult.SUCCESS:
            updated_product = await product_repo.get_with_nutrition_info(product_id)
            
            nutrition_types = [n.nutrition_type for n in updated_product.nutrition_info] if updated_product.nutrition_info else []
            
            # 응답 생성
            response_data = {
                **updated_product.__dict__,
                "current_stock": product.current_stock,
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
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    # 재고 감소
    max_retries = settings.MAX_RETRY_LOCK
    for attempt in range(max_retries):
        result = await product_repo.adjust_admin_stock(product_id, -1)  # 1개 감소
        
        if result == StockUpdateResult.SUCCESS:
            updated_product = await product_repo.get_with_nutrition_info(product_id)
            
            nutrition_types = [n.nutrition_type for n in updated_product.nutrition_info] if updated_product.nutrition_info else []
            
            # 응답 생성
            response_data = {
                **updated_product.__dict__,
                "current_stock": product.current_stock,
                "nutrition_types": nutrition_types
            }
            
            return ProductResponse.model_validate(response_data)
        elif result == StockUpdateResult.INSUFFICIENT_STOCK:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="재고를 더 이상 감소시킬 수 없습니다. 전체 재고가 부족합니다."
            )
        
        if attempt == max_retries - 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="재고 업데이트 중 충돌이 발생했습니다. 다시 시도해주세요."
            )


@router.post("/{product_id}/nutrition", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
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
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
        )
    
    updated_nutrition, duplicates = await nutrition_repo.add_nutrition_with_validation(
        product_id=product_id,
        nutrition_types=request.nutrition_types
    )
    
    # 중복이 있으면 에러 발생
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 존재하는 영양 타입: {', '.join([d.value for d in duplicates])}"
        )
    
    # 응답 생성
    response_data = {
        **product.__dict__,
        "current_stock": product.current_stock,
        "nutrition_types": updated_nutrition
    }
    
    return ProductResponse.model_validate(response_data)


@router.delete("/{product_id}/nutrition", response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
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
    
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    # 상품 조회
    product = await product_repo.get_by_product_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다"
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
        "current_stock": product.current_stock,
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