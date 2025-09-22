from fastapi import HTTPException, status

from api.deps.repository import StoreRepositoryDep
from services.redis_cache import RedisCache


async def get_store_id_by_email(
    seller_email: str,
    store_repo: StoreRepositoryDep
) -> str:
    """
    seller_email로 store_id 조회 (Redis 캐싱 적용)
    
    Args:
        seller_email: 현재 로그인한 판매자 이메일
        store_repo: 가게 레포지토리
    
    Returns:
        str: store_id
    
    Raises:
        HTTPException: 가게를 찾을 수 없는 경우
    """
    # Redis에서 캐시된 store_id 조회
    cached_store_id = await RedisCache.get_store_id(seller_email)
    
    if cached_store_id:
        return cached_store_id
    
    # Redis에 없거나 DB에서 찾을 수 없는 경우, seller_email로 직접 조회
    stores = await store_repo.get_by_seller_email(seller_email)
    
    if not stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    
    # 첫 번째 가게 사용 - (현재 버전은 판매자가 하나의 가게만 가짐)
    store = stores[0]
    
    # Redis에 캐싱
    await RedisCache.set_store_id(seller_email, store.store_id)
    
    return store.store_id