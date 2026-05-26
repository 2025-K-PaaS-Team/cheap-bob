from typing import List, Optional

from app.util.id_generator import generate_store_id
from app.domain.seller.service.exception import StoreAlreadyRegisteredError
from app.domain.seller.repository.store_sns import StoreSNSRepository
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.seller.repository.store_address import StoreAddressRepository
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.model.store import Store
from app.database.session import UnitOfWork, transactional


class SellerStoreRegisterService:
    """1차 회원가입 — Store + Address + SNS + Operation 한 트랜잭션에서 생성.

    각 테이블 INSERT 는 본 서비스가 sub-repository 를 직접 조합해 처리한다.

    payment 정보 등록은 payment 도메인의 `SellerPaymentSettingsService.register` 에 위임 (라우터가 별도로 호출).
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def register(
        self,
        *,
        seller_email: str,
        store_name: str,
        store_introduction: str,
        store_phone: str,
        store_postal_code: str,
        store_address: str,
        store_detail_address: str,
        sido: str,
        sigungu: str,
        bname: str,
        lat: str,
        lng: str,
        nearest_station: Optional[str],
        walking_time: Optional[int],
        sns_info: Optional[dict],
        operation_times: List[dict],
    ) -> Store:
        store_repo = StoreRepository(self._session)
        if await store_repo.get_by_seller_email(seller_email):
            raise StoreAlreadyRegisteredError("이미 가게가 등록된 판매자입니다.")

        address = await StoreAddressRepository(self._session).create(
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            lat=lat,
            lng=lng,
            nearest_station=nearest_station,
            walking_time=walking_time,
        )

        store_id = generate_store_id()
        store = await store_repo.create(
            store_id=store_id,
            store_name=store_name,
            seller_email=seller_email,
            store_introduction=store_introduction,
            store_phone=store_phone,
            store_postal_code=store_postal_code,
            store_address=store_address,
            store_detail_address=store_detail_address,
            address_id=address.address_id,
        )

        if sns_info:
            await StoreSNSRepository(self._session).create(
                store_id=store_id,
                instagram=sns_info.get("instagram"),
                facebook=sns_info.get("facebook"),
                x=sns_info.get("x"),
                homepage=sns_info.get("homepage"),
            )

        await StoreOperationInfoRepository(self._session).create_initial_operation_info(
            store_id=store_id, operation_times=operation_times,
        )

        # payment_info 는 MSA 분리로 backend-payment 가 소유 — refresh 대상 아님.
        await self._session.refresh(
            store, ["address", "sns_info", "operation_info"],
        )
        return store
