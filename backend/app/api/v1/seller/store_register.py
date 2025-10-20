from typing import List
from fastapi import APIRouter, HTTPException, status, UploadFile, File

from utils.id_generator import generate_store_id
from utils.docs_error import create_error_responses
from utils.store_utils import get_store_id_by_email
from api.deps.auth import CurrentSellerDep
from api.deps.repository import StoreRepositoryDep, StorePaymentInfoRepositoryDep
from api.deps.service import ImageServiceDep
from schemas.seller_profile import SellerProfileCreateRequest, SellerProfileResponse, StorePaymentInfoCreateRequest, StorePaymentInfoCheckResponse
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
            nearest_station=request.address_info.nearest_station,
            walking_time=request.address_info.walking_time,
            # Optional info
            sns_info=sns_info,
            operation_times=operation_times_dict
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
        400: ["업로드할 이미지가 없음", "이미지는 최대 11개", "지원하지 않는 파일 형식"],
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
    files: List[UploadFile] = File(..., description="업로드할 이미지 파일들 (첫 번째가 대표 이미지) / 이미지는 최대 11개 / jpeg, jpg, png, webp타입 가능 / 최대 15MB")
):
    """
    가게 이미지 최초 등록
    
    첫 번째 이미지가 대표 이미지로 설정됩니다.
    최대 11개까지 업로드 가능합니다.
    
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
    
    if len(files) > 11:
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


@router.post("/payment", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        409: "이미 결제 정보가 등록되어 있음"
    })
)
async def register_payment_info(
    request: StorePaymentInfoCreateRequest,
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    payment_repo: StorePaymentInfoRepositoryDep
):
    """
    가게 결제 정보 등록
    
    판매자의 가게에 결제 정보를 등록합니다.
    이미 결제 정보가 있는 경우 에러를 반환합니다.
    
    필수 정보:
    - 포트원 가게 ID
    - 포트원 채널 ID
    - 포트원 시크릿 키
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    existing_payment = await payment_repo.exists_by_store_id(store_id)
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 결제 정보가 등록되어 있습니다."
        )
    
    try:
        await payment_repo.create(
            store_id=store_id,
            portone_store_id=request.portone_store_id,
            portone_channel_id=request.portone_channel_id,
            portone_secret_key=request.portone_secret_key
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결제 정보 등록 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/payment", response_model=StorePaymentInfoCheckResponse, status_code=status.HTTP_200_OK,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음"
    })
)
async def check_payment_info(
    current_user: CurrentSellerDep,
    store_repo: StoreRepositoryDep,
    payment_repo: StorePaymentInfoRepositoryDep
):
    """
    가게 결제 정보 확인
    
    판매자의 가게에 결제 정보가 등록되어 있는지 확인합니다.
    """
    seller_email = current_user["sub"]
    
    store_id = await get_store_id_by_email(seller_email, store_repo)
    
    has_payment_info = await payment_repo.exists_by_store_id(store_id)
    
    return StorePaymentInfoCheckResponse(is_exist=has_payment_info)