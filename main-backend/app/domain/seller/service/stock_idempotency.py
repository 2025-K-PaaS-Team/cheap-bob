"""(payment_id, op_type) 기반 stock 조작 멱등화 진입점.

payment-backend 의 internal client retry 가 다음 케이스에서 stock 을 두 번 건드리지 않게 한다:
  - init 의 consume_stock 응답이 timeout 났는데 실제로는 main-backend 가 적용한 경우의 재호출.
  - finalize 보상 / sweep restore 가 중복 트리거된 경우.

stock_operation_log 의 INSERT ON CONFLICT DO NOTHING 으로 dedupe 한 뒤 같은 트랜잭션
에서 실제 stock 조정을 호출한다 — 둘 중 하나가 실패하면 함께 롤백되어 ledger 와 stock 이
어긋날 수 없다.
"""
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.repository.stock_operation_log import (
    StockOperationLogRepository,
)
from app.database.session import UnitOfWork, transactional


_OP_CONSUME = "consume"
_OP_RESTORE = "restore"


class StockIdempotencyService:

    def __init__(
        self,
        uow: UnitOfWork,
        seller_product_service: SellerProductService,
    ):
        self.uow = uow
        self.seller_product_service = seller_product_service


    @transactional
    async def consume(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> bool:
        """첫 호출에서만 실제 차감 — 같은 (payment_id, "consume") 의 재호출은 noop.

        Returns: True = 신규 적용, False = 이미 적용되어 skip.

        Raises: ProductStockInsufficientError / ProductStockConflictError 는 그대로 전파.
        """
        log_repo = StockOperationLogRepository(self._session)
        inserted = await log_repo.try_insert(
            payment_id=payment_id,
            op_type=_OP_CONSUME,
            product_id=product_id,
            quantity=quantity,
        )
        if not inserted:
            return False
        await self.seller_product_service.consume_purchased_stock(
            product_id=product_id, quantity=quantity,
        )
        return True


    @transactional
    async def restore(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> bool:
        """첫 호출에서만 실제 복원 — 같은 (payment_id, "restore") 의 재호출은 noop.

        Returns: True = 신규 적용, False = 이미 적용되어 skip.
        """
        log_repo = StockOperationLogRepository(self._session)
        inserted = await log_repo.try_insert(
            payment_id=payment_id,
            op_type=_OP_RESTORE,
            product_id=product_id,
            quantity=quantity,
        )
        if not inserted:
            return False
        await self.seller_product_service.restore_purchased_stock(
            product_id=product_id, quantity=quantity,
        )
        return True
