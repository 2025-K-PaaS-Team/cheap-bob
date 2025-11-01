from core.redis import RedisClient

class QRCallbackCache:
    """QR 콜백 처리를 위한 Redis 캐시 유틸리티"""
    
    QR_CALLBACK_PREFIX = "qr_callback:"
    WAITING_STATUS = "waiting"
    COMPLETED_STATUS = "completed"
    TTL_SECONDS = 30
    
    @staticmethod
    async def set_waiting_status(payment_id: str) -> None:
        """결제 대기 상태 설정"""
        redis = await RedisClient.get_client()
        key = f"{QRCallbackCache.QR_CALLBACK_PREFIX}{payment_id}"
        await redis.set(key, QRCallbackCache.WAITING_STATUS, ex=QRCallbackCache.TTL_SECONDS)
    
    @staticmethod
    async def set_completed_status(payment_id: str) -> None:
        """결제 완료 상태 설정"""
        redis = await RedisClient.get_client()
        key = f"{QRCallbackCache.QR_CALLBACK_PREFIX}{payment_id}"
        await redis.set(key, QRCallbackCache.COMPLETED_STATUS, ex=QRCallbackCache.TTL_SECONDS)
    
    @staticmethod
    async def get_status(payment_id: str) -> str | None:
        """현재 상태 조회"""
        redis = await RedisClient.get_client()
        key = f"{QRCallbackCache.QR_CALLBACK_PREFIX}{payment_id}"
        return await redis.get(key)
    
    @staticmethod
    async def delete_status(payment_id: str) -> None:
        """상태 삭제"""
        redis = await RedisClient.get_client()
        key = f"{QRCallbackCache.QR_CALLBACK_PREFIX}{payment_id}"
        await redis.delete(key)