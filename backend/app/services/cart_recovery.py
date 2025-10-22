from loguru import logger

from database.session import get_session
from repositories.cart_item import CartItemRepository
from repositories.store_product_info import StoreProductInfoRepository, StockUpdateResult
from config.settings import settings
from database.session import get_db

class CartRecoveryService:
    """서버 재부팅 시 장바구니 재고 복구 서비스"""
    
    @classmethod
    async def recover_abandoned_carts(cls) -> int:
        """
        서버 재부팅 시 모든 장바구니 아이템의 재고를 복구하고 삭제
        
        Returns:
            복구된 장바구니 아이템 수
        """
        recovered_count = 0
        
        try:
            async with get_session() as session:
                cart_repo = CartItemRepository(session)
                product_repo = StoreProductInfoRepository(session)
                
                cart_items = await cart_repo.get_many(load_relations=["product"])
                
                if not cart_items:
                    logger.info("복구할 장바구니 아이템이 없습니다.")
                    return 0
                
                logger.info(f"복구 대상 장바구니 아이템 수: {len(cart_items)}")
                
                for cart_item in cart_items:
                    try:
                        max_retries = settings.MAX_RETRY_LOCK
                        for attempt in range(max_retries):
                            result = await product_repo.adjust_purchased_stock(
                                cart_item.product_id, 
                                -cart_item.quantity
                            )
                            
                            if result == StockUpdateResult.SUCCESS:
                                logger.info(
                                    f"재고 복구 성공 - Payment ID: {cart_item.payment_id}, "
                                    f"Product ID: {cart_item.product_id}, 수량: {cart_item.quantity}"
                                )
                                break
                            elif result == StockUpdateResult.LOCK_CONFLICT:
                                if attempt < max_retries - 1:
                                    logger.warning(
                                        f"재고 복구 재시도 {attempt + 1}/{max_retries} - "
                                        f"Payment ID: {cart_item.payment_id}"
                                    )
                                    continue
                            
                            if attempt == max_retries - 1:
                                logger.error(
                                    f"재고 복구 실패 - Payment ID: {cart_item.payment_id}, "
                                    f"Product ID: {cart_item.product_id}, Result: {result}"
                                )
                                continue
                        
                        deleted = await cart_repo.delete(cart_item.payment_id)
                        if deleted:
                            recovered_count += 1
                            logger.info(f"장바구니 아이템 삭제 완료 - Payment ID: {cart_item.payment_id}")
                        else:
                            logger.error(f"장바구니 아이템 삭제 실패 - Payment ID: {cart_item.payment_id}")
                            
                    except Exception as e:
                        logger.error(
                            f"장바구니 복구 처리 중 오류 - Payment ID: {cart_item.payment_id}, "
                            f"Error: {str(e)}"
                        )
                        continue
                
                await session.commit()
                logger.info(f"장바구니 재고 복구 완료 - 총 {recovered_count}개 아이템 처리")
                
        except Exception as e:
            logger.error(f"장바구니 재고 복구 서비스 오류: {str(e)}")
            raise
        
        return recovered_count