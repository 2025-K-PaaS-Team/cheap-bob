from typing import Annotated, Dict

from fastapi import Depends, HTTPException, Request, status


async def get_current_user(request: Request) -> Dict:
    """현재 인증된 사용자 정보를 반환합니다."""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = request.state.user
    
    if not user.get("is_active"):
        raise HTTPException(
            status_code=439,
            detail="탈퇴한 계정입니다",
            headers={"X-Account-Status": "inactive"}
        )
    
    return user


async def get_current_customer(
    current_user: Annotated[Dict, Depends(get_current_user)]
) -> Dict:
    """Customer 권한을 가진 사용자만 접근 가능"""
    if current_user.get("user_type") != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer 권한이 필요합니다"
        )
    return current_user


async def get_current_seller(
    current_user: Annotated[Dict, Depends(get_current_user)]
) -> Dict:
    """Seller 권한을 가진 사용자만 접근 가능"""
    if current_user.get("user_type") != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller 권한이 필요합니다"
        )
    return current_user


CurrentUserDep = Annotated[Dict, Depends(get_current_user)]
CurrentCustomerDep = Annotated[Dict, Depends(get_current_customer)]
CurrentSellerDep = Annotated[Dict, Depends(get_current_seller)]


async def get_current_user_no_active(request: Request) -> Dict:
    """현재 인증된 사용자 정보를 반환합니다. (탈퇴 인증 X)"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = request.state.user
    
    return user


async def get_current_customer_no_active(
    current_user: Annotated[Dict, Depends(get_current_user_no_active)]
) -> Dict:
    """Customer 권한을 가진 사용자만 접근 가능 (탈퇴 인증 X)"""
    if current_user.get("user_type") != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer 권한이 필요합니다"
        )
    return current_user


async def get_current_seller_no_active(
    current_user: Annotated[Dict, Depends(get_current_user_no_active)]
) -> Dict:
    """Seller 권한을 가진 사용자만 접근 가능 (탈퇴 인증 X)"""
    if current_user.get("user_type") != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller 권한이 필요합니다"
        )
    return current_user


CurrentUserNoActiveDep = Annotated[Dict, Depends(get_current_user_no_active)]
CurrentCustomerNoActiveDep = Annotated[Dict, Depends(get_current_customer_no_active)]
CurrentSellerNoActiveDep = Annotated[Dict, Depends(get_current_seller_no_active)]