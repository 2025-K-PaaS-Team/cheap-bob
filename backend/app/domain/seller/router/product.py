from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerDep
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import (
    ProductAlreadyRegisteredError,
    ProductNotFoundError,
    ProductNutritionDuplicateError,
    ProductNutritionNotFoundError,
    ProductStockConflictError,
    ProductStockInsufficientError,
    ProductStockReservationNotFoundError,
    StoreNotFoundError,
)
from app.domain.seller.schema.product import (
    ProductCreateRequest,
    ProductNutritionRequest,
    ProductResponse,
    ProductStockReservationRequest,
    ProductStockReservationResponse,
    ProductUpdateRequest,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/products", tags=["Seller-Product"])


def _to_response(product, nutrition_types) -> ProductResponse:
    return ProductResponse(
        product_id=product.product_id,
        store_id=product.store_id,
        product_name=product.product_name,
        description=product.description,
        initial_stock=product.initial_stock,
        current_stock=product.current_stock,
        price=product.price,
        sale=product.sale,
        version=product.version,
        nutrition_types=nutrition_types,
    )


@router.post(
    "/register",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
        409: "이미 상품을 등록함",
    }),
)
@inject
async def create_product(
    request: ProductCreateRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        product, nutrition = await product_service.create(
            store_id=store_id,
            product_name=request.product_name,
            description=request.description,
            initial_stock=request.initial_stock,
            price=request.price,
            sale=request.sale,
            nutrition_types=request.nutrition_types,
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductAlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return _to_response(product, nutrition)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음",
    }),
)
@inject
async def get_product(
    product_id: str,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        product, nutrition = await product_service.get(
            store_id=store_id, product_id=product_id,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_response(product, nutrition)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["등록된 가게를 찾을 수 없음", "상품을 찾을 수 없음"],
    }),
)
@inject
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        product, nutrition = await product_service.update(
            store_id=store_id,
            product_id=product_id,
            update_data=request.model_dump(exclude_unset=True),
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_response(product, nutrition)


@router.patch(
    "/{product_id}/stock/up",
    response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음",
        409: "재고 업데이트 중 충돌이 발생",
    }),
)
@inject
async def increase_product_stock(
    product_id: str,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        product, nutrition = await product_service.adjust_admin_stock(
            store_id=store_id, product_id=product_id, delta=1,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductStockConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return _to_response(product, nutrition)


@router.patch(
    "/{product_id}/stock/down",
    response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음",
        409: ["남은 재고가 없음", "재고 업데이트 중 충돌이 발생"],
    }),
)
@inject
async def decrease_product_stock(
    product_id: str,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        product, nutrition = await product_service.adjust_admin_stock(
            store_id=store_id, product_id=product_id, delta=-1,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductStockInsufficientError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ProductStockConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return _to_response(product, nutrition)


@router.get(
    "/{product_id}/stock/reservation",
    response_model=ProductStockReservationResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["상품을 찾을 수 없음", "재고 예약 정보를 찾을 수 없음"],
    }),
)
@inject
async def get_stock_reservation(
    product_id: str,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        reservation = await product_service.get_stock_reservation(
            store_id=store_id, product_id=product_id,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductStockReservationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return ProductStockReservationResponse(
        product_id=reservation.product_id,
        initial_stock=reservation.initial_stock,
        new_stock=reservation.new_stock,
        reserved_at=reservation.reserved_at,
    )


@router.post(
    "/{product_id}/stock/reservation",
    response_model=ProductStockReservationResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음",
        400: "잘못된 재고 예약 요청",
    }),
)
@inject
async def upsert_stock_reservation(
    product_id: str,
    request: ProductStockReservationRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        reservation = await product_service.upsert_stock_reservation(
            store_id=store_id, product_id=product_id, new_stock=request.new_stock,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return ProductStockReservationResponse(
        product_id=reservation.product_id,
        initial_stock=reservation.initial_stock,
        new_stock=reservation.new_stock,
        reserved_at=reservation.reserved_at,
    )


@router.delete(
    "/{product_id}/stock/reservation",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["상품을 찾을 수 없음", "재고 예약 정보를 찾을 수 없음"],
    }),
)
@inject
async def delete_stock_reservation(
    product_id: str,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        await product_service.delete_stock_reservation(
            store_id=store_id, product_id=product_id,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductStockReservationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{product_id}/nutrition",
    response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음",
        400: "이미 존재하는 영양 타입이 있음",
    }),
)
@inject
async def add_product_nutrition(
    product_id: str,
    request: ProductNutritionRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        product, nutrition = await product_service.add_nutrition(
            store_id=store_id,
            product_id=product_id,
            nutrition_types=request.nutrition_types,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductNutritionDuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 존재하는 영양 타입: {', '.join(e.duplicates)}",
        )
    return _to_response(product, nutrition)


@router.delete(
    "/{product_id}/nutrition",
    response_model=ProductResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["상품을 찾을 수 없음", "삭제할 영양 정보를 찾을 수 없음"],
    }),
)
@inject
async def remove_product_nutrition(
    product_id: str,
    request: ProductNutritionRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    product_service: SellerProductService = Depends(Provide["seller_product_service"]),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        product, nutrition = await product_service.remove_nutrition(
            store_id=store_id,
            product_id=product_id,
            nutrition_types=request.nutrition_types,
        )
    except (StoreNotFoundError, ProductNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductNutritionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"존재하지 않는 영양 타입: {', '.join(e.missing)}",
        )
    return _to_response(product, nutrition)
