from typing import List

from app.domain.customer.service.search_history_cache import SearchHistoryCache


class CustomerHistoryService:
    """검색 히스토리 (Redis sorted list). RDB 미사용 — UoW 불필요."""

    async def list_history(self, customer_email: str) -> List[str]:
        return await SearchHistoryCache.get(customer_email)


    async def clear(self, customer_email: str) -> None:
        await SearchHistoryCache.clear(customer_email)


    async def remove(self, customer_email: str, search_name: str) -> bool:
        return await SearchHistoryCache.remove(customer_email, search_name)


    async def record_search(self, customer_email: str, search_name: str) -> None:
        """search 라우터가 키워드 검색 시 호출. 히스토리에 추가."""
        await SearchHistoryCache.add(customer_email, search_name)
