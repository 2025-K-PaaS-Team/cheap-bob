from typing import Literal
from pydantic import HttpUrl
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject

from app.domain.seller.service.seller_store_sns import SellerStoreSNSService
from app.domain.seller.schema.store_sns import StoreSNSResponse, StoreSNSUpdateRequest
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/sns", tags=["Seller-Store-SNS"])

SNSType = Literal["instagram", "facebook", "x", "homepage"]


def _to_response(store_id: str, sns) -> StoreSNSResponse:
    if sns is None:
        return StoreSNSResponse(
            store_id=store_id, instagram=None, facebook=None, x=None, homepage=None,
        )
    return StoreSNSResponse(
        store_id=store_id,
        instagram=HttpUrl(sns.instagram) if sns.instagram else None,
        facebook=HttpUrl(sns.facebook) if sns.facebook else None,
        x=HttpUrl(sns.x) if sns.x else None,
        homepage=HttpUrl(sns.homepage) if sns.homepage else None,
    )


@router.get(
    "",
    response_model=StoreSNSResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def get_store_sns(
    store_id: CurrentSellerStoreIdDep,
    sns_service: SellerStoreSNSService = Depends(Provide["seller_store_sns_service"]),
):
    sns = await sns_service.get(store_id)
    return _to_response(store_id, sns)


@router.put(
    "",
    response_model=StoreSNSResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "등록된 SNS 정보를 찾을 수 없음"],
    }),
)
@inject
async def update_store_sns(
    request: StoreSNSUpdateRequest,
    store_id: CurrentSellerStoreIdDep,
    sns_service: SellerStoreSNSService = Depends(Provide["seller_store_sns_service"]),
):
    updated = await sns_service.update(
        store_id=store_id,
        instagram=str(request.instagram) if request.instagram is not None else None,
        facebook=str(request.facebook) if request.facebook is not None else None,
        x=str(request.x) if request.x is not None else None,
        homepage=str(request.homepage) if request.homepage is not None else None,
    )
    return _to_response(store_id, updated)


@router.delete(
    "/{sns_type}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "등록된 SNS 정보를 찾을 수 없음"],
        422: "잘못된 SNS 유형",
    }),
)
@inject
async def delete_store_sns_field(
    sns_type: SNSType,
    store_id: CurrentSellerStoreIdDep,
    sns_service: SellerStoreSNSService = Depends(Provide["seller_store_sns_service"]),
):
    await sns_service.delete_field(store_id, sns_type)
