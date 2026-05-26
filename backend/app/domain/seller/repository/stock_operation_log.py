"""stock_operation_log INSERT ON CONFLICT DO NOTHING 전용 repository.

읽기/수정은 의도적으로 노출하지 않는다 — 로그는 append-only.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.domain.seller.model.stock_operation_log import StockOperationLog


class StockOperationLogRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def try_insert(
        self,
        *,
        payment_id: str,
        op_type: str,
        product_id: str,
        quantity: int,
    ) -> bool:
        """INSERT 시도. PK 충돌 시 (이미 적용됨) False, 신규 INSERT 시 True.

        같은 트랜잭션 안에서 본 호출이 True 를 반환했다면 동일한 (payment_id, op_type)
        의 후속 호출은 SQL 에러 없이 False 만 반환한다 — 이후 stock 조작도 안전하게 skip 가능.
        """
        stmt = (
            pg_insert(StockOperationLog)
            .values(
                payment_id=payment_id,
                op_type=op_type,
                product_id=product_id,
                quantity=quantity,
            )
            .on_conflict_do_nothing(index_elements=["payment_id", "op_type"])
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
