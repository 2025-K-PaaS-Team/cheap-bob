from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerDep
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_store_image import SellerStoreImageService
from app.domain.seller.service.exception import (
    StoreImageMainDeleteError,
    StoreImageNotFoundError,
    StoreNotFoundError,
)
from app.domain.seller.schema.image import (
    ImageUploadResponse,
    StoreImagesResponse,
    StoreImagesUploadResponse,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/images", tags=["Seller-Store-Images"])

_MAX_IMAGES = 11
_MAX_FILE_SIZE = 15 * 1024 * 1024
_ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


async def _validate_image_files(files: List[UploadFile]) -> list[tuple]:
    validated = []
    for f in files:
        if f.content_type not in _ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 형식입니다: {f.filename}",
            )
        content = await f.read()
        if len(content) > _MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"파일 크기가 너무 큽니다 (최대 15MB): {f.filename}",
            )
        await f.seek(0)
        validated.append((f.file, f.filename, f.content_type))
    return validated


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
    files: List[UploadFile] = File(..., description="추가할 이미지 파일들"),
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    seller_email = current_user["sub"]
    if not files:
        raise HTTPException(status_code=400, detail="업로드할 이미지가 없습니다.")

    try:
        store_id = await store_read_service.get_store_id_by_seller_email(seller_email)
        existing = await image_service.list_images(store_id)
        if len(files) + len(existing) > _MAX_IMAGES:
            raise HTTPException(
                status_code=400,
                detail=f"이미지는 최대 {_MAX_IMAGES}개까지 업로드 가능합니다.",
            )
        validated = await _validate_image_files(files)
        return await image_service.add_images(
            store_id=store_id, seller_email=seller_email, files=validated,
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
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
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        images = await image_service.list_images(store_id)
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

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
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    seller_email = current_user["sub"]
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(seller_email)
        await image_service.delete_image(
            store_id=store_id, seller_email=seller_email, image_id=image_id,
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StoreImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StoreImageMainDeleteError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


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
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    seller_email = current_user["sub"]
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(seller_email)
        return await image_service.change_main_image(
            store_id=store_id, seller_email=seller_email, new_main_image_id=image_id,
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StoreImageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
