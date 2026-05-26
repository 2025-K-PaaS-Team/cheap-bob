from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependency_injector.wiring import Provide, inject
from datetime import date

from app.domain.seller.service.seller_settlement import SellerSettlementService
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.domain.order.schema.settlement import (
    SettlementDayGroup,
    SettlementItem,
    SettlementResponse,
    WeeklyRevenueResponse,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/settlement", tags=["Seller-Settlement"])


@router.get(
    "",
    response_model=SettlementResponse,
    responses=create_error_responses({
        400: "날짜 범위가 올바르지 않음",
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
    }),
)
@inject
async def get_store_settlement(
    store_id: CurrentSellerStoreIdDep,
    start_date: date = Query(..., description="조회 시작일"),
    end_date: date = Query(..., description="조회 종료일"),
    settlement_service: SellerSettlementService = Depends(
        Provide["seller_settlement_service"],
    ),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작일이 종료일보다 늦을 수 없습니다",
        )
    daily = await settlement_service.get_daily_settlement(
        store_id=store_id, start_date=start_date, end_date=end_date,
    )

    return SettlementResponse(
        daily_settlements=[
            SettlementDayGroup(
                date=d["date"],
                items=[
                    SettlementItem(
                        product_name=item["product_name"],
                        quantity=item["quantity"],
                        total_amount=item["total_amount"],
                        status=item["status"],
                        time_at=item["time_at"],
                    )
                    for item in d["items"]
                ],
            )
            for d in daily
        ],
    )


@router.get(
    "/weekly-revenue",
    response_model=WeeklyRevenueResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
    }),
)
@inject
async def get_weekly_revenue(
    store_id: CurrentSellerStoreIdDep,
    settlement_service: SellerSettlementService = Depends(
        Provide["seller_settlement_service"],
    ),
):
    total = await settlement_service.get_weekly_revenue(store_id)

    return WeeklyRevenueResponse(total_revenue=total)
