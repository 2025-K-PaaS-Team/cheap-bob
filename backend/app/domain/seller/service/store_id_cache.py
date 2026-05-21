"""seller 도메인 Redis 캐시 — seller_email → store_id 매핑.

`SellerStoreReadService.get_store_id_by_seller_email` 의 hot path 최적화 (24h TTL).
"""
from typing import Optional

from app.core.redis import RedisClient


class SellerStoreIdCache:
    """seller_email → store_id 매핑 캐시."""

    _PREFIX = "store_id:"
    _DEFAULT_TTL = RedisClient.DEFAULT_CACHE_TTL


    @classmethod
    async def get(cls, seller_email: str) -> Optional[str]:
        redis = await RedisClient.get_client()
        return await redis.get(f"{cls._PREFIX}{seller_email}")


    @classmethod
    async def set(
        cls, seller_email: str, store_id: str, ttl: int = _DEFAULT_TTL,
    ) -> None:
        redis = await RedisClient.get_client()
        await redis.set(f"{cls._PREFIX}{seller_email}", store_id, ex=ttl)


    @classmethod
    async def delete(cls, seller_email: str) -> None:
        redis = await RedisClient.get_client()
        await redis.delete(f"{cls._PREFIX}{seller_email}")
