from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Path
from utils.docs_error import create_error_responses
from api.deps import CurrentSellerDep, AsyncSessionDep
from repositories.store import StoreRepository
from repositories.store_image import StoreImageRepository
from schemas.image import StoreImagesUploadResponse, StoreImagesResponse, ImageUploadResponse
from services.image import ImageService
from core.exceptions import HTTPValueError

router = APIRouter(prefix="/store/images", tags=["Seller-Store-Images"])


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_store_image_repository(session: AsyncSessionDep) -> StoreImageRepository:
    return StoreImageRepository(session)


def get_image_service(session: AsyncSessionDep) -> ImageService:
    return ImageService(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
StoreImageRepositoryDep = Annotated[StoreImageRepository, Depends(get_store_image_repository)]
ImageServiceDep = Annotated[ImageService, Depends(get_image_service)]


async def verify_store_owner(
    store_id: str,
    seller_email: str,
    store_repo: StoreRepositoryDep
) -> None:
    """
    가게 소유권 검증
    """
    store = await store_repo.get_by_store_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    
    if store.seller_email != seller_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가게 이미지를 관리할 권한이 없습니다."
        )


async def validate_image_files(files: List[UploadFile]) -> List[tuple]:
    """
    이미지 파일 검증
    """
    validated_files = []
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    max_size = 10 * 1024 * 1024  # 10MB
    
    for file in files:
        # 파일 타입 검증
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 형식입니다: {file.filename}"
            )
        
        # 파일 크기 검증
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"파일 크기가 너무 큽니다 (최대 10MB): {file.filename}"
            )
        
        # 파일 포인터 리셋
        await file.seek(0)
        
        validated_files.append((file.file, file.filename, file.content_type))
    
    return validated_files


@router.post("/{store_id}", response_model=StoreImagesUploadResponse,
    responses=create_error_responses({
        400: ["업로드할 이미지가 없음", "이미지는 한 번에 최대 5개", "지원하지 않는 파일 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 이미지를 업로드할 권한이 없음",
        404: "가게를 찾을 수 없음",
        413: "파일 크기가 너무 큼"
    })
)
async def add_store_images(
    store_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    image_service: ImageServiceDep,
    files: List[UploadFile] = File(..., description="추가할 이미지 파일들")
):
    """
    가게 이미지 추가
    
    기존 이미지에 추가로 이미지를 업로드합니다.
    최대 5개까지 동시에 업로드 가능합니다.
    
    지원 형식: JPG, JPEG, PNG, WEBP
    최대 크기: 10MB
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드할 이미지가 없습니다."
        )
    
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지는 한 번에 최대 5개까지 업로드 가능합니다."
        )
    
    try:
        # 파일 검증
        validated_files = await validate_image_files(files)
        
        # 이미지 추가
        result = await image_service.add_store_images(
            store_id=store_id,
            seller_email=seller_email,
            files=validated_files
        )
        
        return result
        
    except HTTPValueError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 업로드 중 오류가 발생했습니다: {str(e)}"
        )
    finally:
        # 파일 닫기
        for file in files:
            await file.close()


@router.get("/{store_id}", response_model=StoreImagesResponse,
    responses=create_error_responses({
        404: "가게를 찾을 수 없음"
    })
)
async def get_store_images(
    store_id: str,
    image_service: ImageServiceDep
):
    """
    가게 이미지 목록 조회
    
    가게의 모든 이미지를 조회합니다.
    인증 없이 조회 가능합니다.
    """
    try:
        images = await image_service.get_store_images(store_id)
        
        return StoreImagesResponse(
            store_id=store_id,
            images=images,
            total=len(images)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{store_id}/{image_id:path}", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 이미지를 삭제할 권한이 없음",
        404: "이미지를 찾을 수 없음",
        409: "대표 이미지는 삭제할 수 없음"
    })
)
async def delete_store_image(
    store_id: str,
    image_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    image_service: ImageServiceDep
):
    """
    가게 이미지 삭제
    
    대표 이미지는 삭제할 수 없습니다.
    대표 이미지를 변경하려면 PUT /main/{image_id}를 사용하세요.
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        success = await image_service.delete_store_image(
            store_id=store_id,
            seller_email=seller_email,
            image_id=image_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="이미지 삭제에 실패했습니다."
            )
            
    except HTTPValueError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{store_id}/main/{image_id:path}", response_model=ImageUploadResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "가게 이미지를 변경할 권한이 없음",
        404: ["이미지를 찾을 수 없음", "가게를 찾을 수 없음"]
    })
)
async def change_main_image(
    store_id: str,
    image_id: str,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    image_service: ImageServiceDep
):
    """
    대표 이미지 변경
    
    선택한 기존 이미지를 대표 이미지로 변경합니다.
    """
    seller_email = current_user["sub"]
    
    await verify_store_owner(store_id, seller_email, store_repo)
    
    try:
        result = await image_service.change_main_image(
            store_id=store_id,
            seller_email=seller_email,
            new_main_image_id=image_id
        )
        
        return result
        
    except HTTPValueError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대표 이미지 변경 중 오류가 발생했습니다: {str(e)}"
        )