"""seller 의 가게 결제 정보 등록 / 조회 / 수정."""
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.schema.store_payment_settings import (
    StoreInitPaymentResponse,
    StorePaymentResponse,
)


class SellerPaymentSettingsService:

    def __init__(self, store_payment_info_service: StorePaymentInfoService):
        self.store_payment_info_service = store_payment_info_service


    async def register(
        self,
        *,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
        portone_secret_key: str,
    ) -> None:
        await self.store_payment_info_service.register(
            store_id=store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
            portone_secret_key=portone_secret_key,
        )


    async def exists(self, store_id: str) -> bool:
        return await self.store_payment_info_service.exists_by_store(store_id)


    async def get_initial(self, store_id: str) -> StoreInitPaymentResponse:
        """secret_key 는 응답에서 제외 — 조회는 ID 만 노출."""
        payment_info = await self.store_payment_info_service.find_by_store(store_id)
        return StoreInitPaymentResponse(
            store_id=store_id,
            portone_store_id=payment_info.portone_store_id if payment_info else None,
            portone_channel_id=payment_info.portone_channel_id if payment_info else None,
        )


    async def update_ids(
        self,
        *,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
    ) -> StorePaymentResponse:
        await self.store_payment_info_service.update_portone_ids(
            store_id=store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
        )
        return StorePaymentResponse(
            store_id=store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
        )


    async def rotate_secret_key(
        self, *, store_id: str, portone_secret_key: str,
    ) -> None:
        """PortOne 콘솔에서 secret 을 rotate 했을 때 호출. 응답에 secret 자체는 노출하지 않는다."""
        await self.store_payment_info_service.update_secret_key(
            store_id=store_id, portone_secret_key=portone_secret_key,
        )
