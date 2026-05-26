"""StorePaymentInfo CRUD — payment-svc 의 자체 DB 에서 작동."""
from typing import Optional

from app.domain.payment.service.exception import (
    PaymentInfoAlreadyExistsError,
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
)
from app.domain.payment.repository.store_payment_info import (
    StorePaymentInfoRepository,
)
from app.domain.payment.model.store_payment_info import StorePaymentInfo
from app.database.session import UnitOfWork, transactional


class StorePaymentInfoService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def find_by_store(self, store_id: str) -> Optional[StorePaymentInfo]:
        return await StorePaymentInfoRepository(self._session).get_by_store_id(
            store_id,
        )


    @transactional
    async def get_by_store(self, store_id: str) -> StorePaymentInfo:
        """없으면 `PaymentInfoMissingError`."""
        payment_info = await StorePaymentInfoRepository(
            self._session,
        ).get_by_store_id(store_id)
        if payment_info is None:
            raise PaymentInfoMissingError("가게의 결제 설정이 완료되지 않았습니다")
        return payment_info


    @transactional
    async def get_complete_by_store(self, store_id: str) -> StorePaymentInfo:
        """모든 portone_* 필드가 채워진 경우만 반환. 누락이면 `PaymentInfoIncompleteError`."""
        payment_info = await self.get_by_store(store_id)
        if not (
            payment_info.portone_store_id
            and payment_info.portone_channel_id
            and payment_info.portone_secret_key
        ):
            raise PaymentInfoIncompleteError(
                "포트원 결제 설정이 완료되지 않았습니다",
            )
        return payment_info


    @transactional
    async def exists_by_store(self, store_id: str) -> bool:
        return await StorePaymentInfoRepository(self._session).exists_by_store_id(
            store_id,
        )


    @transactional
    async def register(
        self,
        *,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
        portone_secret_key: str,
    ) -> None:
        repo = StorePaymentInfoRepository(self._session)
        if await repo.exists_by_store_id(store_id):
            raise PaymentInfoAlreadyExistsError(
                "이미 결제 정보가 등록되어 있습니다.",
            )
        await repo.create(
            store_id=store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
            portone_secret_key=portone_secret_key,
        )


    @transactional
    async def has_complete_info(self, store_id: str) -> bool:
        return await StorePaymentInfoRepository(self._session).has_complete_info(
            store_id,
        )


    @transactional
    async def delete_by_store(self, store_id: str) -> bool:
        repo = StorePaymentInfoRepository(self._session)
        if not await repo.exists_by_store_id(store_id):
            return False
        await repo.delete(store_id)
        return True


    @transactional
    async def update_portone_ids(
        self,
        *,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
    ) -> StorePaymentInfo:
        return await StorePaymentInfoRepository(
            self._session,
        ).update_portone_info(
            store_id=store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
        )


    @transactional
    async def update_secret_key(
        self, *, store_id: str, portone_secret_key: str,
    ) -> StorePaymentInfo:
        return await StorePaymentInfoRepository(
            self._session,
        ).update_secret_key(store_id, portone_secret_key)
