from fastapi import APIRouter, status, HTTPException
from urllib.parse import unquote

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentCustomerDep
from schemas.search_history import SearchHistoryResponse
from services.redis_cache import SearchHistoryCache

router = APIRouter(prefix="/history", tags=["Customer-Search-History"])


@router.get("/search", response_model=SearchHistoryResponse,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_search_history(
    current_user: CurrentCustomerDep
):
    """
    검색 히스토리 조회 API
    
    소비자의 최근 검색어 목록을 조회 (최대 5개)
    """
    customer_email = current_user["sub"]
    
    history = await SearchHistoryCache.get_search_history(customer_email)
    
    return SearchHistoryResponse(
        search_names=history,
        count=len(history)
    )


@router.delete("/search", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"]
    })
)
async def clear_search_history(
    current_user: CurrentCustomerDep
):
    """
    검색 히스토리 삭제 API
    
    소비자의 모든 검색 히스토리를 삭제
    """
    
    customer_email = current_user["sub"]
    
    await SearchHistoryCache.clear_search_history(customer_email)
    
    return None


@router.delete("/search/{search_name}", status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401:["인증 정보가 없음", "토큰 만료"],
        404:"검색어를 찾을 수 없음"
    })
)
async def remove_search_name(
    search_name: str,
    current_user: CurrentCustomerDep
):
    """
    특정 검색어 삭제 API
    
    소비자의 검색 히스토리에서 특정 검색어만 삭제
    """
    customer_email = current_user["sub"]
    
    # URL 디코딩
    decoded_search_name = unquote(search_name)
    
    removed = await SearchHistoryCache.remove_search_name(
        customer_email, 
        decoded_search_name
    )
    
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="검색어를 찾을 수 없습니다"
        )
    
    return None