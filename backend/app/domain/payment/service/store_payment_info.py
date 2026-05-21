"""StorePaymentInfo CRUD — seller settings + customer payment + order refund 가 모두 본 서비스 경유."""
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
        """포트원 모든 필드 (store_id, channel_id, secret_key) 가 채워진 경우만 반환.

        결제 init/refund 시 사용 — 누락이면 `PaymentInfoIncompleteError`.
        """
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
        """가게 1차 가입 시 결제 정보 최초 등록 (이미 있으면 충돌)."""
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
        """포트원 모든 필드가 채워져 있는지 boolean 으로 반환. 예외 안 던짐.

        스케줄러 worker / 운영 상태 batch 가 가게 단위 결제 등록 여부를 빠르게 확인할 때 사용.
        """
        return await StorePaymentInfoRepository(self._session).has_complete_info(
            store_id,
        )


    @transactional
    async def delete_by_store(self, store_id: str) -> bool:
        """탈퇴 cleanup 시 호출. 대상이 없으면 False.

        cross-domain (seller withdraw) 진입점 — payment.repository 직접 import 회피.
        """
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
        """settings 화면에서 ID 만 갱신 (secret_key 는 별도 경로)."""
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
        """secret_key rotate — seller 가 PortOne 콘솔에서 키를 갱신했을 때 호출."""
        return await StorePaymentInfoRepository(
            self._session,
        ).update_secret_key(store_id, portone_secret_key)
