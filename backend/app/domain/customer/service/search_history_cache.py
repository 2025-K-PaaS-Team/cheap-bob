"""customer 도메인 Redis 캐시 — 검색어 히스토리.

`CustomerHistoryService` 가 호출. 최대 5개 / 7일 TTL.
"""
from typing import List
import json

from app.core.redis import RedisClient


class SearchHistoryCache:
    """customer_email → 최근 검색어 5개 (LRU)."""

    _PREFIX = "search_history:"
    _MAX_SIZE = 5
    _TTL_SECONDS = 7 * 24 * 60 * 60


    @classmethod
    async def add(cls, customer_email: str, search_name: str) -> None:
        redis = await RedisClient.get_client()
        key = f"{cls._PREFIX}{customer_email}"
        history_json = await redis.get(key)
        history = json.loads(history_json) if history_json else []
        history = [t for t in history if t != search_name]
        history.insert(0, search_name)
        history = history[: cls._MAX_SIZE]
        await redis.set(key, json.dumps(history), ex=cls._TTL_SECONDS)


    @classmethod
    async def get(cls, customer_email: str) -> List[str]:
        """getex 로 TTL 갱신하면서 조회 — '본 사용자 활동 중' 의 signal."""
        redis = await RedisClient.get_client()
        key = f"{cls._PREFIX}{customer_email}"
        history_json = await redis.getex(key, ex=cls._TTL_SECONDS)
        return json.loads(history_json) if history_json else []


    @classmethod
    async def clear(cls, customer_email: str) -> None:
        redis = await RedisClient.get_client()
        await redis.delete(f"{cls._PREFIX}{customer_email}")


    @classmethod
    async def remove(cls, customer_email: str, search_name: str) -> bool:
        redis = await RedisClient.get_client()
        key = f"{cls._PREFIX}{customer_email}"
        history_json = await redis.get(key)
        if not history_json:
            return False
        history = json.loads(history_json)
        if search_name not in history:
            return False
        history = [t for t in history if t != search_name]
        if history:
            await redis.set(key, json.dumps(history), ex=cls._TTL_SECONDS)
        else:
            await redis.delete(key)
        return True
