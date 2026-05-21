"""결제 5분 timeout 스케줄러.

`schedule_payment_timeout` 이 APScheduler 에 1회성 job 을 등록한다. 5분 내에 confirm 되면
`remove_payment_schedule` 로 job 을 취소; timeout 발화 시 콜백이 재고 복구 + 장바구니 삭제.
"""
from pytz import timezone as pytz_timezone
from loguru import logger
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.domain.seller.service.seller_product import SellerProductService
from app.domain.order.service.order_query import OrderQueryService


_KST = pytz_timezone("Asia/Seoul")
_TIMEOUT_MINUTES = 5


class PaymentSchedulerService:

    def __init__(
        self,
        scheduler: AsyncIOScheduler,
        seller_product_service: SellerProductService,
        order_query_service: OrderQueryService,
    ):
        self.scheduler = scheduler
        self.seller_product_service = seller_product_service
        self.order_query_service = order_query_service


    async def schedule_payment_timeout(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> bool:
        """5분 후 타임아웃 콜백 등록. 콜백은 재고 복구 + 장바구니 삭제."""
        job_id = f"payment_timeout_{payment_id}"
        run_time = datetime.now(_KST) + timedelta(minutes=_TIMEOUT_MINUTES)

        async def _on_timeout():
            logger.info("결제 타임아웃 — 재고 복구 시작 (payment_id={})", payment_id)
            try:
                await self.seller_product_service.restore_purchased_stock(
                    product_id=product_id, quantity=quantity,
                )
            except Exception as e:
                logger.error("재고 복구 실패: {}", e)
            try:
                await self.order_query_service.delete_cart_item(payment_id)
            except Exception as e:
                logger.error("장바구니 삭제 실패: {}", e)

        try:
            self.scheduler.add_job(
                func=_on_timeout,
                trigger="date",
                run_date=run_time,
                id=job_id,
                name=f"Payment timeout for {payment_id}",
                misfire_grace_time=60,
                replace_existing=True,
            )
            logger.info(
                "결제 타임아웃 스케줄 등록 (payment_id={}, run_at={})",
                payment_id, run_time,
            )
            return True
        except Exception as e:
            logger.error("결제 타임아웃 등록 실패: {}", e)
            return False


    def remove_payment_schedule(self, payment_id: str) -> bool:
        """confirm 성공 시 호출 — 등록된 타임아웃 job 제거. 없으면 False."""
        job_id = f"payment_timeout_{payment_id}"
        try:
            job = self.scheduler.get_job(job_id)
            if job is None:
                logger.warning("삭제할 스케줄 없음 (payment_id={})", payment_id)
                return False
            self.scheduler.remove_job(job_id)
            return True
        except Exception as e:
            logger.error("결제 스케줄 제거 실패: {}", e)
            return False
