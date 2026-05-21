from datetime import datetime, timedelta, timezone

from app.domain.seller.service.seller_account import SellerAccountService
from app.domain.seller.service.exception import (
    SellerAlreadyActiveError,
    SellerAlreadyWithdrawnError,
    SellerStoreOpenError,
    SellerWithdrawalRecordNotFoundError,
)
from app.domain.seller.repository.store_sns import StoreSNSRepository
from app.domain.seller.repository.store_product_info import StoreProductInfoRepository
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.seller.repository.store_image import StoreImageRepository
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.repository.seller_withdraw_reservation import (
    SellerWithdrawReservationRepository,
)
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.database.session import UnitOfWork, transactional
from app.core.logger import get_logger


_KST = timezone(timedelta(hours=9))


logger = get_logger("seller.service.seller_withdraw")


class SellerWithdrawService:
    """판매자 탈퇴 / 탈퇴 취소.

    오늘 영업 여부 — seller.OperationInfoRepository (own domain). is_active 토글 —
    `SellerAccountService` (own domain).
    """

    def __init__(
        self,
        uow: UnitOfWork,
        withdraw_repo: SellerWithdrawReservationRepository,
        seller_account_service: SellerAccountService,
        store_payment_info_service: StorePaymentInfoService,
    ):
        self.uow = uow
        self.withdraw_repo = withdraw_repo
        self.seller_account_service = seller_account_service
        self.store_payment_info_service = store_payment_info_service


    async def request_withdraw(self, *, seller_email: str, store_id: str) -> None:
        await self._assert_not_open_today(store_id)
        if not await self.seller_account_service.is_active(seller_email):
            raise SellerAlreadyWithdrawnError("이미 탈퇴 처리 되었습니다.")

        await self.seller_account_service.set_active(seller_email, active=False)
        await self.withdraw_repo.save(
            seller_email=seller_email, withdrawn_at=datetime.now(timezone.utc),
        )


    async def cancel_withdraw(self, seller_email: str) -> None:
        if await self.seller_account_service.is_active(seller_email):
            raise SellerAlreadyActiveError("이미 활성화된 계정입니다.")

        record = await self.withdraw_repo.find_by_seller_email(seller_email)
        if record is None:
            raise SellerWithdrawalRecordNotFoundError("탈퇴 기록을 찾을 수 없습니다.")

        await self.seller_account_service.set_active(seller_email, active=True)
        await self.withdraw_repo.delete_by_seller_email(seller_email)


    @transactional
    async def _assert_not_open_today(self, store_id: str) -> None:
        today_dow = datetime.now(_KST).weekday()
        op = await StoreOperationInfoRepository(self._session).get_by_store_and_day(
            store_id, today_dow,
        )
        if op is not None and op.is_currently_open:
            raise SellerStoreOpenError("가게 오픈 상태여서 탈퇴할 수 없습니다")


    async def process_pending_withdrawals(self) -> int:
        """예약된 seller 탈퇴 row 를 hard-delete 로 확정. 호출자: worker.

        가게 자산 (Store / Product / Operation / Image / SNS) + `StorePaymentInfo` +
        `Seller` 순서로 정리. 일부 cascade 가 부족해 명시적 삭제 필요.
        한 건 실패가 batch 를 무산시키지 않도록 per-item swallow.

        Returns: 실제 처리된 seller 수.
        """
        reservations = await self.withdraw_repo.get_many()
        if not reservations:
            return 0

        processed = 0
        for reservation in reservations:
            email = reservation.seller_email
            try:
                if await self._hard_delete_seller_with_stores(email):
                    processed += 1
                await self.withdraw_repo.delete_by_id(str(reservation.id))
            except Exception:
                logger.exception("판매자 {} 탈퇴 처리 중 오류", email)
        return processed


    @transactional
    async def _hard_delete_seller_with_stores(self, email: str) -> bool:
        """가게 자산 cascade 정리 + Seller hard-delete. 호출자: process_pending_withdrawals."""
        store_repo = StoreRepository(self._session)
        product_repo = StoreProductInfoRepository(self._session)
        op_repo = StoreOperationInfoRepository(self._session)
        image_repo = StoreImageRepository(self._session)
        sns_repo = StoreSNSRepository(self._session)

        stores = await store_repo.get_by_seller_email(email)
        for store in stores:
            logger.info("가게 {} (ID: {}) 삭제", store.store_name, store.store_id)
            for product in await product_repo.get_by_store_id(store.store_id):
                await product_repo.delete(product.product_id)

            await self.store_payment_info_service.delete_by_store(store.store_id)

            for op in await op_repo.get_many(
                filters={"store_id": store.store_id},
            ):
                await self._session.delete(op)
            for img in await image_repo.get_by_store_id(store.store_id):
                await self._session.delete(img)
            sns_info = await sns_repo.get_by_store_id(store.store_id)
            if sns_info:
                await self._session.delete(sns_info)

            await store_repo.delete(store.store_id)

        deleted = await self.seller_account_service.hard_delete(email)
        if deleted:
            logger.info("판매자 {} 탈퇴 처리 완료", email)
        else:
            logger.warning("판매자 {}을(를) 찾을 수 없습니다", email)
        return deleted
