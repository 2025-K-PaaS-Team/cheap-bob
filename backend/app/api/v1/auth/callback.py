from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from utils.docs_error import create_error_responses

from api.deps.service import (
    OAuthServiceDep,
    JWTServiceDep
)
from api.deps.repository import StoreRepositoryDep, StoreProductInfoRepositoryDep, CustomerDetailRepositoryDep

from config.oauth import OAuthProvider
from config.settings import settings
from schemas.auth import UserType

router = APIRouter()

async def get_customer_register(
    customer_email: str,
    customer_detail_repo: CustomerDetailRepositoryDep,
) -> str:
    """Customer 2차 등록 정보 가져오는 함수"""
    
    # 소비자 상세 정보 존재 여부 확인
    customer_detail = await customer_detail_repo.get_by_customer(customer_email)
    
    if customer_detail is None:
        # 상세 정보가 등록되지 않은 경우
        registration_status = "profile"
    else:
        # 모든 등록이 완료된 경우
        registration_status = "complete"
        
    return registration_status

async def get_seller_register(
    seller_email: str,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
) -> str:
    """Seller 2차 등록 정보 가져오는 함수"""
    
    existing_stores = await store_repo.get_by_seller_email(seller_email)
        
    if not existing_stores:
        # 가게가 등록되지 않은 경우
        registration_status = "store"
    else:
        # 가게가 등록된 경우, 상품 등록 여부 확인
        store = existing_stores[0]  # 첫 번째 가게 사용
        product_count = await product_repo.count_products_by_store(store.store_id)
        
        if product_count == 0:
            # 상품이 등록되지 않은 경우
            registration_status = "product"
        else:
            # 모든 등록이 완료된 경우
            registration_status = "complete"
        
    return registration_status

@router.get("/{provider}/callback/customer",
    responses=create_error_responses({         
        400:"Oauth 로그인 에러가 발생"
    })   
)
async def customer_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    customer_detail_repo: CustomerDetailRepositoryDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    oauth_service: OAuthServiceDep,
    jwt_service: JWTServiceDep,
    code: str = Query(...),
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    """Customer OAuth 로그인 콜백"""
    try:
        token_response, conflict = await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.CUSTOMER
        )
        
        decoded_token = jwt_service.decode_access_token(token_response.access_token)
        email = decoded_token["sub"]
        
        if conflict:
            registration_status = await get_seller_register(email, store_repo, product_repo)
        else:
            registration_status = await get_customer_register(email,customer_detail_repo)
        
        # 프론트 로컬 개발 용
        if state == '1004':
            frontend_url = settings.FRONTEND_LOCAL_URL
        else:
            frontend_url = settings.FRONTEND_URL
            
        # status 파라미터를 포함한 redirect URL 생성
        response = RedirectResponse(
            url=f"{frontend_url}/auth/success?token={token_response.access_token}&status={registration_status}&conflict={int(conflict)}"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{provider}/callback/seller",
    responses=create_error_responses({         
        400:"Oauth 로그인 에러가 발생",
        403:"탈퇴한 회원임"
    })
)
async def seller_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    customer_detail_repo: CustomerDetailRepositoryDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    oauth_service: OAuthServiceDep,
    jwt_service: JWTServiceDep,
    code: str = Query(...),
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    """Seller OAuth 로그인 콜백"""
    try:
        token_response, conflict = await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.SELLER
        )
        
        # JWT 토큰을 디코드하여 판매자 이메일 추출
        decoded_token = jwt_service.decode_access_token(token_response.access_token)
        email = decoded_token["sub"]
        
        if conflict:
            registration_status = await get_customer_register(email,customer_detail_repo)
        else:
            registration_status = await get_seller_register(email, store_repo, product_repo)
        
        # 프론트 로컬 개발 용
        if state == '1004':
            frontend_url = settings.FRONTEND_LOCAL_URL
        else:
            frontend_url = settings.FRONTEND_URL
            
        response = RedirectResponse(
            url=f"{frontend_url}/auth/success?token={token_response.access_token}&status={registration_status}&conflict={int(conflict)}"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )