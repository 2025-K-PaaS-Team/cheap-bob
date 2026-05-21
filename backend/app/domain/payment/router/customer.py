from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep
from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
    PaymentNotFoundError,
    PaymentOwnershipMismatchError,
    PaymentTimeoutError,
    PaymentVerificationError,
    PickupTimeEndedError,
    ProductNotFoundError,
    StockConflictError,
    StockInsufficientError,
    StoreNotOpenError,
)
from app.domain.payment.service.customer_payment import CustomerPaymentService
from app.domain.payment.schema.customer_payment import (
    PaymentConfirmRequest,
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentResponse,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/customer/payment", tags=["Customer-Payment"])


@router.post(
    "/init",
    response_model=PaymentInitResponse,
    responses=create_error_responses({
        400: ["재고가 없음", "가게가 현재 영업 중이 아님", "픽업 시간이 종료됨"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "상품을 찾을 수 없음",
        409: "동시성 충돌 발생",
        500: "가게의 결제 설정이 완료되지 않음",
    }),
)
@inject
async def init_payment(
    request: PaymentInitRequest,
    current_user: CurrentCustomerDep,
    customer_payment_service: CustomerPaymentService = Depends(
        Provide["customer_payment_service"],
    ),
):
    """결제 초기화 — 재고 차감 + 장바구니 등록 + 5분 타임아웃 스케줄."""
    try:
        return await customer_payment_service.init_payment(
            customer_email=current_user["sub"],
            product_id=request.product_id,
            quantity=request.quantity,
        )
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (StoreNotOpenError, PickupTimeEndedError, StockInsufficientError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except StockConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except (PaymentInfoMissingError, PaymentInfoIncompleteError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e),
        )


@router.post(
    "/confirm",
    response_model=PaymentResponse,
    responses=create_error_responses({
        400: ["결제 검증 실패", "픽업 시간 마감"],
        401: ["인증 정보가 없음", "토큰 만료"],
        403: "결제 권한 없음",
        404: ["결제 정보 없음", "상품 정보 없음"],
        408: "결제 타임아웃",
    }),
)
@inject
async def confirm_payment(
    request: PaymentConfirmRequest,
    current_user: CurrentCustomerDep,
    background_tasks: BackgroundTasks,
    customer_payment_service: CustomerPaymentService = Depends(
        Provide["customer_payment_service"],
    ),
):
    """결제 최종 확인 — PortOne 검증 + 주문 생성 + 장바구니 삭제. 실패 시 자동 환불 + 복구."""
    try:
        return await customer_payment_service.confirm_payment(
            customer_email=current_user["sub"],
            payment_id=request.payment_id,
            background_tasks=background_tasks,
        )
    except PaymentTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=str(e),
        )
    except PaymentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PaymentOwnershipMismatchError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (StoreNotOpenError, PickupTimeEndedError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (PaymentInfoMissingError, PaymentInfoIncompleteError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e),
        )
    except PaymentVerificationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
