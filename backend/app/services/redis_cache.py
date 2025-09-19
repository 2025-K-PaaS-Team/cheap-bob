from typing import Optional
from app.core.redis import RedisClient


class RedisCache:
    """Redis 캐시 관련 유틸리티 클래스"""
    
    STORE_ID_PREFIX = "store_id:"
    
    @staticmethod
    async def get_store_id(seller_email: str) -> Optional[str]:
        """
        seller_email을 기반으로 Redis에서 store_id 조회
        
        Args:
            seller_email: 판매자 이메일
            
        Returns:
            store_id 또는 None
        """
        redis = await RedisClient.get_client()
        key = f"{RedisCache.STORE_ID_PREFIX}{seller_email}"
        store_id = await redis.get(key)
        
        if store_id:
            return store_id
        return None
    
    @staticmethod
    async def set_store_id(seller_email: str, store_id: str, ttl: int = RedisClient.DEFAULT_CACHE_TTL) -> None:
        """
        seller_email을 키로 store_id를 Redis에 저장
        
        Args:
            seller_email: 판매자 이메일
            store_id: 가게 ID
            ttl: Time To Live (초 단위, 기본값: 24시간)
        """
        redis = await RedisClient.get_client()
        key = f"{RedisCache.STORE_ID_PREFIX}{seller_email}"
        await redis.set(key, store_id, ex=ttl)
    
    @staticmethod
    async def delete_store_id(seller_email: str) -> None:
        """
        Redis에서 store_id 캐시 삭제
        
        Args:
            seller_email: 판매자 이메일
        """
        redis = await RedisClient.get_client()
        key = f"{RedisCache.STORE_ID_PREFIX}{seller_email}"
        await redis.delete(key)