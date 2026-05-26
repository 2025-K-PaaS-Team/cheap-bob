from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from dependency_injector.wiring import Provide, inject
import asyncio

from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.domain.order.service.seller_order import SellerOrderService
from app.domain.order.service.qr_callback_cache import QRCallbackCacheService
from app.domain.order.service.exception import (
    OrderNotFoundError,
    OrderOwnershipMismatchError,
)
from app.domain.order.schema.order import (
    OrderCancelRequest,
    OrderCancelResponse,
    OrderItemResponse,
    OrderListResponse,
    SellerPickupQRResponse,
)
from app.domain.order.schema.dashboard import DashboardResponse
from app.domain.auth.dto.auth import UserType
from app.core.openapi import create_error_responses
from app.container import container
from app.config.setting import settings


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
    store_id: CurrentSellerStoreIdDep,
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    """가게 주문 — 당일(RDB) + 과거(Mongo) 통합."""
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
    store_id: CurrentSellerStoreIdDep,
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    return await seller_order_service.list_today_orders(store_id)


@router.patch(
    "/{payment_id}/accept",
    response_model=OrderItemResponse,
    responses=create_error_responses({
        400: "이미 처리한 주문",
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "본인 가게 주문 아님",
        404: "등록된 가게를 찾을 수 없음",
    }),
)
@inject
async def update_order_accept(
    payment_id: str,
    store_id: CurrentSellerStoreIdDep,
    background_tasks: BackgroundTasks,
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    return await seller_order_service.accept_order(
        store_id=store_id,
        payment_id=payment_id,
        background_tasks=background_tasks,
    )


@router.delete(
    "/{payment_id}/cancel",
    response_model=OrderCancelResponse,
    responses=create_error_responses({
        400: "이미 취소한 주문",
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "본인 가게 주문 아님",
        404: "등록된 가게를 찾을 수 없음",
        409: "재고 복구 중, 충돌 발생",
    }),
)
@inject
async def cancel_order(
    payment_id: str,
    request: OrderCancelRequest,
    store_id: CurrentSellerStoreIdDep,
    background_tasks: BackgroundTasks,
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    return await seller_order_service.cancel_order(
        store_id=store_id,
        payment_id=payment_id,
        reason=request.reason,
        background_tasks=background_tasks,
    )


@router.get(
    "/{payment_id}/qr",
    response_model=SellerPickupQRResponse,
    responses=create_error_responses({
        400: "픽업 준비가 되지 않은 주문",
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "본인 가게 주문 아님",
        404: "주문을 찾을 수 없음",
    }),
)
@inject
async def get_order_qr(
    payment_id: str,
    store_id: CurrentSellerStoreIdDep,
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    """30초 유효 픽업 QR — 만료는 QR payload (encode_qr_data) 가 갖는 timestamp 로 검증."""
    return await seller_order_service.get_pickup_qr(
        store_id=store_id, payment_id=payment_id,
    )


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
    store_id: CurrentSellerStoreIdDep,
    seller_order_service: SellerOrderService = Depends(
        Provide["seller_order_service"],
    ),
):
    """대시보드 — 상품별 재고 / 구매 / 조정 현황."""
    return await seller_order_service.get_dashboard(store_id)


def _extract_ws_token(websocket: WebSocket) -> str | None:
    """WebSocket 은 BaseHTTPMiddleware 가 동작하지 않으므로 토큰을 직접 추출.

    dev 환경 한정으로 ?token=... query param 도 허용 (HTTP 미들웨어와 동일 정책).
    """
    if settings.ENVIRONMENT == "dev":
        token = websocket.query_params.get("token")
        if token:
            return token
    return websocket.cookies.get("access_token")


@router.websocket("/{payment_id}/qr/callback")
async def qr_callback_websocket(websocket: WebSocket, payment_id: str):
    """30초 동안 QR 콜백 상태를 polling. 픽업 완료 시 신호 송신 후 종료.

    인증/인가는 accept() 이전에 처리 — 통과 못하면 1008 로 즉시 close.
    DI 는 worker 와 동일하게 container 직접 호출 (BaseHTTPMiddleware/Depends 가
    WebSocket 에서 신뢰성 있게 동작하지 않으므로).
    """
    token = _extract_ws_token(websocket)
    payload = container.jwt_service().decode_access_token(token) if token else None
    if payload is None or payload.get("user_type") != UserType.SELLER.value:
        await websocket.close(code=1008, reason="인증 실패")
        return
    try:
        store_id = await container.seller_store_read_service(
        ).get_store_id_by_seller_email(payload["sub"])
        await container.seller_order_service().assert_order_belongs_to_store(
            store_id=store_id, payment_id=payment_id,
        )
    except (OrderNotFoundError, OrderOwnershipMismatchError):
        await websocket.close(code=1008, reason="권한 없음")
        return
    except Exception:
        # 예상치 못한 인증/인가 단계 오류는 절대 leak 하지 않고 일괄 1008.
        await websocket.close(code=1008, reason="인증 확인 실패")
        return

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
