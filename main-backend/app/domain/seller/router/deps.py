"""seller 도메인 라우터용 공용 dependency.

seller 가 인증된 상태에서 본인의 ``store_id`` 가 필요할 때 매번 ``current_user`` 추출 →
``get_store_id_by_seller_email`` 호출을 반복하지 않도록 한 Dependency 로 묶는다.
다른 도메인 (order, payment) 라우터에서도 본 모듈을 import 해서 쓴다.

``StoreNotFoundError`` 등 도메인 예외는 전역 핸들러 (``app.core.exceptions``) 가 변환하므로
본 Dependency 안에서 try/except 를 두지 않는다.
"""
from typing import Annotated
from fastapi import Depends

from app.middleware.auth import CurrentSellerDep
from app.container import container


async def _current_seller_store_id(current_user: CurrentSellerDep) -> str:
    return await container.seller_store_read_service().get_store_id_by_seller_email(
        current_user["sub"],
    )


CurrentSellerStoreIdDep = Annotated[str, Depends(_current_seller_store_id)]
