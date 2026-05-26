from datetime import datetime, timezone

from app.domain.order.service.order_query import OrderQueryService
from app.domain.customer.service.exception import (
    CustomerActiveOrdersExistError,
    CustomerAlreadyActiveError,
    CustomerAlreadyWithdrawnError,
    WithdrawalRecordNotFoundError,
)
from app.domain.customer.service.customer_account import CustomerAccountService
from app.domain.customer.repository.customer_withdraw_reservation import (
    CustomerWithdrawReservationRepository,
)
from app.database.session import UnitOfWork
from app.core.logger import get_logger


logger = get_logger("customer.service.customer_withdraw")


class CustomerWithdrawService:
    """소비자 탈퇴 신청 / 취소.

    진행 중인 주문 검사 → `OrderQueryService`, is_active 토글 → `CustomerAccountService`.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        withdraw_repo: CustomerWithdrawReservationRepository,
        order_query_service: OrderQueryService,
        customer_account_service: CustomerAccountService,
    ):
        self.uow = uow
        self.withdraw_repo = withdraw_repo
        self.order_query_service = order_query_service
        self.customer_account_service = customer_account_service


    async def request_withdraw(self, customer_email: str) -> None:
        if not await self.customer_account_service.is_active(customer_email):
            raise CustomerAlreadyWithdrawnError("이미 탈퇴 처리 되었습니다.")

        if await self.order_query_service.has_active_orders_for_customer(customer_email):
            raise CustomerActiveOrdersExistError(
                "진행 중인 주문이 있어 탈퇴할 수 없습니다",
            )

        # RDB (is_active=False) ↔ Mongo (reservation insert) 는 분리된 데이터 저장소이므로
        # 단일 트랜잭션으로 묶을 수 없다. reservation insert 가 실패하면 is_active 를 다시
        # True 로 되돌리는 보상 트랜잭션으로 일관성을 맞춘다.
        await self.customer_account_service.set_active(customer_email, active=False)
        try:
            await self.withdraw_repo.save(
                customer_email=customer_email,
                withdrawn_at=datetime.now(timezone.utc),
            )
        except Exception:
            try:
                await self.customer_account_service.set_active(
                    customer_email, active=True,
                )
            except Exception:
                logger.exception(
                    "탈퇴 보상 실패 — customer={} 가 reservation 없이 비활성 상태로 남음",
                    customer_email,
                )
            raise


    async def process_pending_withdrawals(self) -> int:
        """예약된 탈퇴 row 를 hard-delete 로 확정. 호출자: worker.

        각 reservation 처리는 `CustomerAccountService.hard_delete` (자체 트랜잭션) →
        Mongo reservation 삭제 순. 한 건 실패가 전체 batch 를 무산시키지 않도록 per-item swallow.

        Returns: 실제 삭제 처리된 customer 수 (대상 부재로 skip 한 reservation 은 제외).
        """
        reservations = await self.withdraw_repo.get_many()
        if not reservations:
            return 0

        processed = 0
        for reservation in reservations:
            email = reservation.customer_email
            try:
                deleted = await self.customer_account_service.hard_delete(email)
                await self.withdraw_repo.delete_by_id(str(reservation.id))
                if deleted:
                    processed += 1
                    logger.info("소비자 {} 탈퇴 처리 완료", email)
                else:
                    logger.warning("소비자 {}을(를) 찾을 수 없습니다", email)
            except Exception:
                logger.exception("소비자 {} 탈퇴 처리 중 오류", email)
        return processed


    async def cancel_withdraw(self, customer_email: str) -> None:
        if await self.customer_account_service.is_active(customer_email):
            raise CustomerAlreadyActiveError("이미 활성화된 계정입니다")

        record = await self.withdraw_repo.find_by_customer_email(customer_email)
        if record is None:
            raise WithdrawalRecordNotFoundError("탈퇴 기록을 찾을 수 없습니다")

        await self.customer_account_service.set_active(customer_email, active=True)
        await self.withdraw_repo.delete_by_customer_email(customer_email)
