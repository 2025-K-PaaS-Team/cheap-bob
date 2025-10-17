from datetime import datetime, timedelta, timezone
from typing import Any
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone as pytz_timezone

from services.scheduler import scheduler as app_scheduler
from repositories.store_product_info import StockUpdateResult
from config.settings import settings

KST = pytz_timezone('Asia/Seoul')

class PaymentSchedulerService:
    """결제 시간 제한 관리 서비스"""
    
    PAYMENT_TIMEOUT_MINUTES = 5
    
    @classmethod
    def _get_scheduler(cls) -> AsyncIOScheduler:
        """현재 실행 중인 스케줄러 인스턴스 반환"""
        return app_scheduler.scheduler
    
    @classmethod
    async def schedule_payment_timeout(
        cls,
        payment_id: str,
        product_id: str,
        quantity: int,
        product_repo: Any
    ) -> bool:
        """
        결제 타임아웃 스케줄 등록
        5분 후에 재고 복구 작업을 실행하도록 스케줄링
        
        Args:
            payment_id: 결제 ID
            product_id: 상품 ID
            quantity: 구매 수량
            product_repo: 상품 레포지토리 인스턴스
            
        Returns:
            성공 여부
        """
        try:
            scheduler = cls._get_scheduler()
            job_id = f"payment_timeout_{payment_id}"
            
            run_time = datetime.now(KST) + timedelta(minutes=cls.PAYMENT_TIMEOUT_MINUTES)
            
            async def restore_stock():
                """재고 복구 작업"""
                logger.info(f"결제 타임아웃으로 재고 복구 시작 - Payment ID: {payment_id}")
                
                max_retries = settings.MAX_RETRY_LOCK
                for attempt in range(max_retries):
                    result = await product_repo.adjust_purchased_stock(product_id, -quantity)
                    
                    if result == StockUpdateResult.SUCCESS:
                        logger.info(f"재고 복구 성공 - Product ID: {product_id}, 수량: {quantity}")
                        return
                    
                    if attempt == max_retries - 1:
                        logger.error(f"재고 복구 실패 - Product ID: {product_id}, 수량: {quantity}")
            
            scheduler.add_job(
                func=restore_stock,
                trigger='date',
                run_date=run_time,
                id=job_id,
                name=f"Payment timeout for {payment_id}",
                misfire_grace_time=60,
                replace_existing=True
            )
            
            logger.info(f"결제 타임아웃 스케줄 등록 - Payment ID: {payment_id}, 실행 시간: {run_time}")
            return True
            
        except Exception as e:
            logger.error(f"결제 타임아웃 스케줄 등록 실패 - Payment ID: {payment_id}, Error: {str(e)}")
            return False
    
    @classmethod
    def remove_payment_schedule(cls, payment_id: str) -> bool:
        """
        특정 결제의 스케줄 삭제
        
        Args:
            payment_id: 결제 ID
            
        Returns:
            성공 여부
        """
        try:
            scheduler = cls._get_scheduler()
            job_id = f"payment_timeout_{payment_id}"
            
            job = scheduler.get_job(job_id)
            if not job:
                logger.warning(f"삭제할 스케줄이 없음 - Payment ID: {payment_id}")
                return False
            
            scheduler.remove_job(job_id)
            logger.info(f"결제 스케줄 삭제 완료 - Payment ID: {payment_id}")
            return True
            
        except Exception as e:
            logger.error(f"결제 스케줄 삭제 실패 - Payment ID: {payment_id}, Error: {str(e)}")
            return False