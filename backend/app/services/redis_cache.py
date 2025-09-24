from typing import Optional, List
import json
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


class SearchHistoryCache:
    """검색 히스토리 캐시 관련 유틸리티 클래스"""
    
    SEARCH_HISTORY_PREFIX = "search_history:"
    MAX_HISTORY_SIZE = 5
    
    @staticmethod
    async def add_search_name(user_email: str, search_name: str) -> None:
        """
        사용자의 검색어를 히스토리에 추가
        
        Args:
            user_email: 사용자 이메일
            search_name: 검색어
        """
        redis = await RedisClient.get_client()
        key = f"{SearchHistoryCache.SEARCH_HISTORY_PREFIX}{user_email}"
        
        history_json = await redis.get(key)
        history = json.loads(history_json) if history_json else []
        
        history = [term for term in history if term != search_name]
        
        history.insert(0, search_name)
        
        # 최대 5개까지만 유지
        history = history[:SearchHistoryCache.MAX_HISTORY_SIZE]
        
        # Redis에 저장 (7일 TTL)
        await redis.set(key, json.dumps(history), ex=7*24*60*60)
    
    @staticmethod
    async def get_search_history(user_email: str) -> List[str]:
        """
        사용자의 검색 히스토리 조회
        
        Args:
            user_email: 사용자 이메일
            
        Returns:
            검색어 리스트
        """
        redis = await RedisClient.get_client()
        key = f"{SearchHistoryCache.SEARCH_HISTORY_PREFIX}{user_email}"
        
        # getex로 TTL 갱신하면서 조회
        history_json = await redis.getex(key, ex=7*24*60*60)
        return json.loads(history_json) if history_json else []
    
    @staticmethod
    async def clear_search_history(user_email: str) -> None:
        """
        사용자의 검색 히스토리 삭제
        
        Args:
            user_email: 사용자 이메일
        """
        redis = await RedisClient.get_client()
        key = f"{SearchHistoryCache.SEARCH_HISTORY_PREFIX}{user_email}"
        await redis.delete(key)
    
    @staticmethod
    async def remove_search_name(user_email: str, search_name: str) -> bool:
        """
        사용자의 검색 히스토리에서 특정 검색어 삭제
        
        Args:
            user_email: 사용자 이메일
            search_name: 삭제할 검색어
            
        Returns:
            삭제 성공 여부
        """
        redis = await RedisClient.get_client()
        key = f"{SearchHistoryCache.SEARCH_HISTORY_PREFIX}{user_email}"
        
        history_json = await redis.get(key)
        if not history_json:
            return False
            
        history = json.loads(history_json)
        
        if search_name not in history:
            return False
        
        history = [term for term in history if term != search_name]
        
        if not history:
            await redis.delete(key)
        else:
            await redis.set(key, json.dumps(history), ex=7*24*60*60)
            
        return True