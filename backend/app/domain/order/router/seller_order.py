from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from dependency_injector.wiring import Provide, inject
import asyncio

from app.middleware.auth import CurrentSellerDep
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.order.service.seller_order import SellerOrderService
from app.domain.order.service.qr_callback_cache import QRCallbackCacheService
from app.domain.order.service.exception import (
    OrderAlreadyCanceledError,
    OrderNotFoundError,
    OrderNotInReservationError,
    OrderRefundError,
    OrderStockConflictError,
)
from app.domain.order.schema.order import (
    OrderCancelRequest,
    OrderCancelResponse,
    OrderItemResponse,
    OrderListResponse,
    SellerPickupQRResponse,
)
from app.domain.order.schema.dashboard import DashboardResponse
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/seller/store/orders", tags=["Seller-Order"])


@router.get(
    "",
    response_model=OrderListResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
    }),
)
@inject
async def get_store_orders(
    current_user: CurrentSellerDep,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    """가게 주문 — 당일(RDB) + 과거(Mongo) 통합."""
    store_id = await seller_store_read_service.get_store_id_by_seller_email(
        current_user["sub"],
    )
    return await seller_order_service.list_orders(store_id)


@router.get(
    "/today",
    response_model=OrderListResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
    }),
)
@inject
async def get_order_today(
    current_user: CurrentSellerDep,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    store_id = await seller_store_read_service.get_store_id_by_seller_email(
        current_user["sub"],
    )
    return await seller_order_service.list_today_orders(store_id)


@router.patch(
    "/{payment_id}/accept",
    response_model=OrderItemResponse,
    responses=create_error_responses({
        400: "이미 처리한 주문",
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
    }),
)
@inject
async def update_order_accept(
    payment_id: str,
    current_user: CurrentSellerDep,
    background_tasks: BackgroundTasks,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    store_id = await seller_store_read_service.get_store_id_by_seller_email(
        current_user["sub"],
    )
    try:
        return await seller_order_service.accept_order(
            store_id=store_id,
            payment_id=payment_id,
            background_tasks=background_tasks,
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OrderNotInReservationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{payment_id}/cancel",
    response_model=OrderCancelResponse,
    responses=create_error_responses({
        400: "이미 취소한 주문",
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
        409: "재고 복구 중, 충돌 발생",
    }),
)
@inject
async def cancel_order(
    payment_id: str,
    request: OrderCancelRequest,
    current_user: CurrentSellerDep,
    background_tasks: BackgroundTasks,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    store_id = await seller_store_read_service.get_store_id_by_seller_email(
        current_user["sub"],
    )
    try:
        return await seller_order_service.cancel_order(
            store_id=store_id,
            payment_id=payment_id,
            reason=request.reason,
            background_tasks=background_tasks,
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OrderAlreadyCanceledError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OrderRefundError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e),
        )
    except OrderStockConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/{payment_id}/qr",
    response_model=SellerPickupQRResponse,
    responses=create_error_responses({
        400: "픽업 준비가 되지 않은 주문",
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "주문을 찾을 수 없음",
    }),
)
@inject
async def get_order_qr(
    payment_id: str,
    current_user: CurrentSellerDep,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    """30초 유효 픽업 QR — 만료는 QR payload (encode_qr_data) 가 갖는 timestamp 로 검증."""
    store_id = await seller_store_read_service.get_store_id_by_seller_email(
        current_user["sub"],
    )
    try:
        return await seller_order_service.get_pickup_qr(
            store_id=store_id, payment_id=payment_id,
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OrderNotInReservationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "등록된 가게를 찾을 수 없음",
    }),
)
@inject
async def get_dashboard(
    current_user: CurrentSellerDep,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    """대시보드 — 상품별 재고 / 구매 / 조정 현황."""
    store_id = await seller_store_read_service.get_store_id_by_seller_email(
        current_user["sub"],
    )
    return await seller_order_service.get_dashboard(store_id)


@router.websocket("/{payment_id}/qr/callback")
async def qr_callback_websocket(websocket: WebSocket, payment_id: str):
    """30초 동안 QR 콜백 상태를 polling. 픽업 완료 시 신호 송신 후 종료."""
    await websocket.accept()
    try:
        await QRCallbackCacheService.set_waiting(payment_id)

        for _ in range(31):
            try:
                current_status = await QRCallbackCacheService.get(payment_id)
                if current_status is None:
                    await websocket.send_json({
                        "status": "error",
                        "message": "Payment ID를 찾을 수 없습니다. 다시 시도 해주세요.",
                    })
                    return
                if current_status == QRCallbackCacheService.COMPLETED_STATUS:
                    await websocket.send_json({
                        "status": "completed",
                        "message": "Payment completed successfully",
                    })
                    return
                await asyncio.sleep(1)
            except Exception as e:
                await websocket.send_json({"status": "error", "message": str(e)})
                return

        await websocket.send_json({
            "status": "timeout",
            "message": "Connection timeout after 30 seconds",
        })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"status": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        await QRCallbackCacheService.delete(payment_id)
        try:
            await websocket.close()
        except Exception:
            pass
