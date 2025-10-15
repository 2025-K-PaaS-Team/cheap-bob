from typing import List
from fastapi import APIRouter, HTTPException, status, UploadFile, File

from utils.id_generator import generate_store_id
from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import StoreRepositoryDep
from api.deps.service import ImageServiceDep
from schemas.seller_profile import SellerProfileCreateRequest, SellerProfileResponse
from schemas.image import StoreImagesUploadResponse
from core.exceptions import HTTPValueError

router = APIRouter(prefix="/store/register", tags=["Seller-Store-Register"])



@router.post("", response_model=SellerProfileResponse, status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        409: ["이미 가게가 등록된 판매자"]
    })
)
async def register_seller_store(
    request: SellerProfileCreateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep
):
    """
    판매자 1차 가게 등록 회원가입 완료
    
    판매자 인증 후 가게 정보를 포함한 전체 회원가입을 완료합니다.
    
    필수 정보:
    - 매장 기본 정보 (이름, 설명, 전화번호)
    - SNS 정보 (홈페이지, 인스타그램, 페이스북, X)
    - 주소 정보 (우편번호, 주소, 상세주소, 위도, 경도)
    - 운영 정보 (월요일~일요일 운영 시간)
    """
    
    seller_email = current_user["sub"]
    
    # 이미 가게가 등록되어 있는지 확인
    existing_stores = await store_repo.get_by_seller_email(seller_email)
    if existing_stores:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가게가 등록된 판매자입니다."
        )
    
    try:
        store_id = generate_store_id()
        
        # SNS 정보
        sns_info = None
        if request.sns_info:
            sns_info = {
                "instagram": str(request.sns_info.instagram) if request.sns_info.instagram else None,
                "facebook": str(request.sns_info.facebook) if request.sns_info.facebook else None,
                "x": str(request.sns_info.x) if request.sns_info.x else None,
                "homepage": str(request.sns_info.homepage) if request.sns_info.homepage else None
            }
        
        # 운영 정보
        operation_times_dict = [
            {
                'day_of_week': op_time.day_of_week,
                'open_time': op_time.open_time,
                'close_time': op_time.close_time,
                'pickup_start_time': op_time.pickup_start_time,
                'pickup_end_time': op_time.pickup_end_time,
                'is_open_enabled': op_time.is_open_enabled
            }
            for op_time in request.operation_times
        ]
        
        # 결제 정보
        payment_data = {
            "portone_store_id": request.payment_info.portone_store_id,
            "portone_channel_id": request.payment_info.portone_channel_id,
            "portone_secret_key": request.payment_info.portone_secret_key
        }
        
        # 통합 생성
        store = await store_repo.create_store_with_full_info(
            store_id=store_id,
            store_name=request.store_name,
            seller_email=seller_email,
            store_introduction=request.store_introduction,
            store_phone=request.store_phone,
            store_postal_code=request.address_info.postal_code,
            store_address=request.address_info.address,
            store_detail_address=request.address_info.detail_address,
            # Address info
            sido=request.address_info.sido,
            sigungu=request.address_info.sigungu,
            bname=request.address_info.bname,
            lat=request.address_info.lat,
            lng=request.address_info.lng,
            # Optional info
            sns_info=sns_info,
            operation_times=operation_times_dict,
            payment_info=payment_data
        )
        
        # 성공 응답
        return SellerProfileResponse(
            store_id=store.store_id,
            store_name=store.store_name
        )
        
    except ValueError as e:
        # 비즈니스 로직 에러
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # 예상치 못한 에러
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"판매자 회원가입 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 이미지 업로드 관련 엔드포인트
@router.post("/images", response_model=StoreImagesUploadResponse, status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["업로드할 이미지가 없음", "이미지는 한 번에 최대 5개", "지원하지 않는 파일 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        409: "이미 등록된 이미지가 있음",
        413: "파일 크기가 너무 큼"
    })
)
async def register_store_images(
    current_user: CurrentSellerDep,
    image_service: ImageServiceDep,
    store_repo: StoreRepositoryDep,
    files: List[UploadFile] = File(..., description="업로드할 이미지 파일들 (첫 번째가 대표 이미지) / 한 번에 이미지 최대 10개 / jpeg, jpg, png, webp타입 가능 / 최대 15MB")
):
    """
    가게 이미지 최초 등록
    
    첫 번째 이미지가 대표 이미지로 설정됩니다.
    최대 10개까지 업로드 가능합니다.
    
    지원 형식: JPG, JPEG, PNG, WEBP
    최대 크기: 15MB
    """
    seller_email = current_user["sub"]

    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드할 이미지가 없습니다."
        )
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지는 최대 10개까지 업로드 가능합니다."
        )
    
    # 파일 검증 및 준비
    validated_files = []
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    max_size = 15 * 1024 * 1024  # 15MB
    
    try:
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
                    detail=f"파일 크기가 너무 큽니다 (최대 15MB): {file.filename}"
                )
            
            # 파일 포인터 리셋
            await file.seek(0)
            
            validated_files.append((file.file, file.filename, file.content_type))
        
        # 이미지 업로드
        result = await image_service.init_store_images(
            store_id=store_id,
            seller_email=current_user["sub"],
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