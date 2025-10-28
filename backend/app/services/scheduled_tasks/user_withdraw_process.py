import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from database.session import get_session
from repositories.seller_withdraw_reservation import SellerWithdrawReservationRepository
from repositories.customer_withdraw_reservation import CustomerWithdrawReservationRepository
from repositories.seller import SellerRepository
from repositories.customer import CustomerRepository
from repositories.store import StoreRepository
from repositories.store_product_info import StoreProductInfoRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from repositories.store_operation_info import StoreOperationInfoRepository
from repositories.store_image import StoreImageRepository
from repositories.store_sns import StoreSNSRepository


logger = logging.getLogger(__name__)

# KST 타임존 설정
KST = timezone(timedelta(hours=9))


class UserWithdrawProcessTask:
    """사용자 탈퇴 예약 정보를 기반으로 계정 및 관련 데이터를 삭제하는 스케줄 작업"""

    @staticmethod
    async def process_scheduled_withdrawals():
        """매일 새벽 5시 10분에 예약된 사용자 탈퇴 처리"""
        logger.info("=== 예약된 사용자 탈퇴 처리 시작 ===")
        start_time = datetime.now(timezone.utc)
        
        seller_count = await UserWithdrawProcessTask._process_seller_withdrawals()
        customer_count = await UserWithdrawProcessTask._process_customer_withdrawals()
        
        elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            f"=== 예약된 사용자 탈퇴 처리 완료: "
            f"판매자 {seller_count}명, 소비자 {customer_count}명 처리됨 "
            f"(소요시간: {elapsed_time:.2f}초) ==="
        )

    @staticmethod
    async def _process_seller_withdrawals() -> int:
        """판매자 탈퇴 처리"""
        processed_count = 0
        
        try:
            seller_withdraw_repo = SellerWithdrawReservationRepository()
            all_reservations = await seller_withdraw_repo.get_many()
            
            if not all_reservations:
                logger.info("처리할 판매자 탈퇴 예약이 없습니다")
                return 0
            
            logger.info(f"총 {len(all_reservations)}건의 판매자 탈퇴 예약 발견")
            
            async with get_session() as session:
                seller_repo = SellerRepository(session)
                store_repo = StoreRepository(session)
                product_repo = StoreProductInfoRepository(session)
                payment_info_repo = StorePaymentInfoRepository(session)
                operation_info_repo = StoreOperationInfoRepository(session)
                image_repo = StoreImageRepository(session)
                sns_repo = StoreSNSRepository(session)
                
                for reservation in all_reservations:
                    try:
                        seller_email = reservation.seller_email
                        logger.info(f"판매자 {seller_email} 탈퇴 처리 시작")
                        
                        seller = await seller_repo.get_by_email(seller_email)
                        if not seller:
                            logger.warning(f"판매자 {seller_email}을(를) 찾을 수 없습니다")
                            await seller_withdraw_repo.delete_by_id(str(reservation.id))
                            continue
                        
                        stores = await store_repo.get_by_seller_email(seller_email)
                        
                        for store in stores:
                            logger.info(f"가게 {store.store_name} (ID: {store.store_id}) 관련 데이터 삭제 시작")
                            
                            products = await product_repo.get_by_store_id(store.store_id)
                            for product in products:
                                await product_repo.delete(product.product_id)
                            
                            payment_info = await payment_info_repo.get_by_store_id(store.store_id)
                            if payment_info:
                                await payment_info_repo.delete(payment_info.store_id)
                            
                            operation_infos = await operation_info_repo.get_many(filters={"store_id": store.store_id})
                            for op_info in operation_infos:
                                await session.delete(op_info)
                            
                            images = await image_repo.get_by_store_id(store.store_id)
                            for image in images:
                                await session.delete(image)
                            
                            sns_info = await sns_repo.get_by_store_id(store.store_id)
                            if sns_info:
                                await session.delete(sns_info)
                            
                            await store_repo.delete(store.store_id)
                            logger.info(f"가게 {store.store_name} 삭제 완료")
                        
                        await seller_repo.delete(seller_email)
                        
                        await seller_withdraw_repo.delete_by_id(str(reservation.id))
                        
                        processed_count += 1
                        logger.info(f"판매자 {seller_email} 탈퇴 처리 완료")
                        
                    except Exception as e:
                        logger.error(
                            f"판매자 {reservation.seller_email} 탈퇴 처리 중 오류 발생: {str(e)}",
                            exc_info=True
                        )
                        continue
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"판매자 탈퇴 처리 중 오류 발생: {e}", exc_info=True)
            
        return processed_count

    @staticmethod
    async def _process_customer_withdrawals() -> int:
        """소비자 탈퇴 처리"""
        processed_count = 0
        
        try:
            customer_withdraw_repo = CustomerWithdrawReservationRepository()
            all_reservations = await customer_withdraw_repo.get_many()
            
            if not all_reservations:
                logger.info("처리할 소비자 탈퇴 예약이 없습니다")
                return 0
            
            logger.info(f"총 {len(all_reservations)}건의 소비자 탈퇴 예약 발견")
            
            async with get_session() as session:
                customer_repo = CustomerRepository(session)
                
                for reservation in all_reservations:
                    try:
                        customer_email = reservation.customer_email
                        logger.info(f"소비자 {customer_email} 탈퇴 처리 시작")
                        
                        customer = await customer_repo.get_by_email(customer_email)
                        if not customer:
                            logger.warning(f"소비자 {customer_email}을(를) 찾을 수 없습니다")
                            await customer_withdraw_repo.delete_by_id(str(reservation.id))
                            continue
                        
                        await customer_repo.delete(customer_email)
                        
                        await customer_withdraw_repo.delete_by_id(str(reservation.id))
                        
                        processed_count += 1
                        logger.info(f"소비자 {customer_email} 탈퇴 처리 완료")
                        
                    except Exception as e:
                        logger.error(
                            f"소비자 {reservation.customer_email} 탈퇴 처리 중 오류 발생: {str(e)}",
                            exc_info=True
                        )
                        continue
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"소비자 탈퇴 처리 중 오류 발생: {e}", exc_info=True)
            
        return processed_count

    @staticmethod
    async def force_process_withdrawals_now() -> Dict[str, Any]:
        """수동으로 탈퇴 처리를 즉시 실행 (테스트/관리 목적)"""
        logger.info("수동 탈퇴 처리 요청됨")
        
        try:
            await UserWithdrawProcessTask.process_scheduled_withdrawals()
            return {
                "success": True,
                "message": "탈퇴 처리가 성공적으로 완료되었습니다"
            }
        except Exception as e:
            logger.error(f"수동 탈퇴 처리 실패: {e}")
            return {
                "success": False,
                "message": f"탈퇴 처리 실패: {str(e)}"
            }


# 스케줄러에 등록할 태스크 정의
scheduled_task = {
    "func": UserWithdrawProcessTask.process_scheduled_withdrawals,
    "trigger": "cron",
    "trigger_args": {
        "hour": 4,
        "minute": 40,
    },
    "job_id": "process_user_withdrawals",
    "job_name": "예약된 사용자 탈퇴 처리",
    "misfire_grace_time": 3600,
}