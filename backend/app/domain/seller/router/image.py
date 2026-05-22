from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from dependency_injector.wiring import Provide, inject

from app.util.image_validator import validate_image_files
from app.middleware.auth import CurrentSellerDep
from app.domain.seller.service.seller_store_image import SellerStoreImageService
from app.domain.seller.schema.image import (
    ImageUploadResponse,
    StoreImagesResponse,
    StoreImagesUploadResponse,
)
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/images", tags=["Seller-Store-Images"])

_MAX_IMAGES = 11


@router.post(
    "",
    response_model=StoreImagesUploadResponse,
    responses=create_error_responses({
        400: ["업로드할 이미지가 없음", f"이미지는 최대 {_MAX_IMAGES}개", "지원하지 않는 파일 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        413: "파일 크기가 너무 큼",
    }),
)
@inject
async def add_store_images(
    current_user: CurrentSellerDep,
    store_id: CurrentSellerStoreIdDep,
    files: List[UploadFile] = File(..., description="추가할 이미지 파일들"),
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    seller_email = current_user["sub"]
    if not files:
        raise HTTPException(status_code=400, detail="업로드할 이미지가 없습니다.")

    try:
        existing = await image_service.list_images(store_id)
        if len(files) + len(existing) > _MAX_IMAGES:
            raise HTTPException(
                status_code=400,
                detail=f"이미지는 최대 {_MAX_IMAGES}개까지 업로드 가능합니다.",
            )
        validated = await validate_image_files(files)
        return await image_service.add_images(
            store_id=store_id, seller_email=seller_email, files=validated,
        )
    finally:
        for f in files:
            await f.close()


@router.get(
    "",
    response_model=StoreImagesResponse,
    responses=create_error_responses({404: "가게를 찾을 수 없음"}),
)
@inject
async def get_store_images(
    store_id: CurrentSellerStoreIdDep,
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    images = await image_service.list_images(store_id)

    return StoreImagesResponse(store_id=store_id, images=images, total=len(images))


@router.delete(
    "/{image_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "이미지를 찾을 수 없음",
        409: "대표 이미지는 삭제할 수 없음",
    }),
)
@inject
async def delete_store_image(
    image_id: str,
    current_user: CurrentSellerDep,
    store_id: CurrentSellerStoreIdDep,
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    seller_email = current_user["sub"]
    await image_service.delete_image(
        store_id=store_id, seller_email=seller_email, image_id=image_id,
    )


@router.put(
    "/main/{image_id:path}",
    response_model=ImageUploadResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["이미지를 찾을 수 없음", "가게를 찾을 수 없음"],
    }),
)
@inject
async def change_main_image(
    image_id: str,
    current_user: CurrentSellerDep,
    store_id: CurrentSellerStoreIdDep,
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    seller_email = current_user["sub"]
    return await image_service.change_main_image(
        store_id=store_id, seller_email=seller_email, new_main_image_id=image_id,
    )
