"""QR 콜백 상태 (Redis). 픽업 완료 신호를 ws 채널과 동기화한다."""
from typing import Optional

from app.core.redis import RedisClient


class QRCallbackCacheService:
    _PREFIX = "qr_callback:"
    WAITING_STATUS = "waiting"
    COMPLETED_STATUS = "completed"
    TTL_SECONDS = 30


    @classmethod
    def _key(cls, payment_id: str) -> str:
        return f"{cls._PREFIX}{payment_id}"


    @classmethod
    async def set_waiting(cls, payment_id: str) -> None:
        redis = await RedisClient.get_client()
        await redis.set(cls._key(payment_id), cls.WAITING_STATUS, ex=cls.TTL_SECONDS)


    @classmethod
    async def set_completed(cls, payment_id: str) -> None:
        redis = await RedisClient.get_client()
        await redis.set(cls._key(payment_id), cls.COMPLETED_STATUS, ex=cls.TTL_SECONDS)


    @classmethod
    async def get(cls, payment_id: str) -> Optional[str]:
        redis = await RedisClient.get_client()
        return await redis.get(cls._key(payment_id))


    @classmethod
    async def delete(cls, payment_id: str) -> None:
        redis = await RedisClient.get_client()
        await redis.delete(cls._key(payment_id))
