from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep
from app.domain.order.service.exception import (
    OrderAlreadyCanceledError,
    OrderAlreadyCompletedError,
    OrderNotAcceptedError,
    OrderNotFoundError,
    OrderNotInReservationError,
    OrderOwnershipMismatchError,
    OrderQrInvalidError,
    OrderRefundError,
    OrderStockConflictError,
)
from app.domain.order.service.customer_order import CustomerOrderService
from app.domain.order.schema.order import (
    CustomerOrderListResponse,
    CustomerPickupCompleteRequest,
    CustomerTodayOrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse,
    OrderItemResponse,
    TodayAlarmResponse,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/customer/orders", tags=["Customer-Order"])


@router.get(
    "",
    response_model=CustomerOrderListResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_order_history(
    current_user: CurrentCustomerDep,
    customer_order_service: CustomerOrderService = Depends(
        Provide["customer_order_service"],
    ),
):
    """주문 내역 — 당일(RDB) + 과거(Mongo) 통합."""
    return await customer_order_service.list_orders(current_user["sub"])


@router.get(
    "/today",
    response_model=CustomerTodayOrderListResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_order_today(
    current_user: CurrentCustomerDep,
    customer_order_service: CustomerOrderService = Depends(
        Provide["customer_order_service"],
    ),
):
    """당일 주문 + 오늘 요일의 가게 픽업 시간."""
    return await customer_order_service.list_today_orders(current_user["sub"])


@router.get(
    "/today-alarm",
    response_model=TodayAlarmResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_today_alarm(
    current_user: CurrentCustomerDep,
    customer_order_service: CustomerOrderService = Depends(
        Provide["customer_order_service"],
    ),
):
    """주문 상태 전이 시각별 알림 카드 (reservation_at / accepted_at / canceled_at)."""
    return await customer_order_service.get_today_alarm(current_user["sub"])


@router.get(
    "/{payment_id}",
    response_model=OrderItemResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "주문을 찾을 수 없음",
    }),
)
@inject
async def get_order_detail(
    payment_id: str,
    current_user: CurrentCustomerDep,
    customer_order_service: CustomerOrderService = Depends(
        Provide["customer_order_service"],
    ),
):
    try:
        return await customer_order_service.get_detail(payment_id)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{payment_id}/complete",
    response_model=OrderItemResponse,
    responses=create_error_responses({
        400: ["유효하지 않은 QR 코드", "권한이 없는 소비자", "이미 픽업 완료"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["주문을 찾을 수 없음", "QR 코드를 찾을 수 없음"],
    }),
)
@inject
async def complete_pickup(
    payment_id: str,
    request: CustomerPickupCompleteRequest,
    current_user: CurrentCustomerDep,
    customer_order_service: CustomerOrderService = Depends(
        Provide["customer_order_service"],
    ),
):
    try:
        return await customer_order_service.complete_pickup(
            customer_email=current_user["sub"],
            payment_id=payment_id,
            qr_data=request.qr_data,
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OrderAlreadyCompletedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OrderNotAcceptedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (OrderQrInvalidError, OrderOwnershipMismatchError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{payment_id}/cancel",
    response_model=OrderCancelResponse,
    responses=create_error_responses({
        400: ["이미 취소된 주문", "이미 승인된 주문"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음",
        409: "동시성 충돌 발생",
    }),
)
@inject
async def cancel_order(
    payment_id: str,
    request: OrderCancelRequest,
    current_user: CurrentCustomerDep,
    background_tasks: BackgroundTasks,
    customer_order_service: CustomerOrderService = Depends(
        Provide["customer_order_service"],
    ),
):
    try:
        return await customer_order_service.cancel(
            customer_email=current_user["sub"],
            payment_id=payment_id,
            reason=request.reason,
            background_tasks=background_tasks,
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OrderAlreadyCanceledError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OrderNotInReservationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OrderRefundError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e),
        )
    except OrderStockConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
