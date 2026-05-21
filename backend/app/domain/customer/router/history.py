from urllib.parse import unquote
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep
from app.domain.customer.service.customer_history import CustomerHistoryService
from app.domain.customer.schema.search_history import SearchHistoryResponse
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/history", tags=["Customer-Search-History"])


@router.get(
    "/search",
    response_model=SearchHistoryResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_search_history(
    current_user: CurrentCustomerDep,
    history_service: CustomerHistoryService = Depends(
        Provide["customer_history_service"],
    ),
):
    """최근 검색어 (최대 5개)."""
    history = await history_service.list_history(current_user["sub"])
    return SearchHistoryResponse(search_names=history, count=len(history))


@router.delete(
    "/search",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def clear_search_history(
    current_user: CurrentCustomerDep,
    history_service: CustomerHistoryService = Depends(
        Provide["customer_history_service"],
    ),
):
    await history_service.clear(current_user["sub"])
    return None


@router.delete(
    "/search/{search_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["검색어를 찾을 수 없음"],
    }),
)
@inject
async def remove_search_name(
    search_name: str,
    current_user: CurrentCustomerDep,
    history_service: CustomerHistoryService = Depends(
        Provide["customer_history_service"],
    ),
):
    decoded = unquote(search_name)
    removed = await history_service.remove(current_user["sub"], decoded)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="검색어를 찾을 수 없습니다",
        )
    return None
