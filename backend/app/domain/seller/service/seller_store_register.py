from typing import Optional

from app.util.id_generator import generate_store_id
from app.domain.seller.service.exception import StoreAlreadyRegisteredError
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.model.store import Store
from app.database.session import UnitOfWork, transactional


class SellerStoreRegisterService:
    """1차 회원가입 — Store + Address + SNS + Operation 한 트랜잭션 생성.

    payment 정보 등록은 payment 도메인의 `SellerPaymentSettingsService.register` 에 위임 (router 가
    별도로 호출). 본 서비스는 가게 메타데이터 생성만 책임진다.
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
        operation_times: list[dict],
    ) -> Store:
        repo = StoreRepository(self._session)
        existing = await repo.get_by_seller_email(seller_email)
        if existing:
            raise StoreAlreadyRegisteredError("이미 가게가 등록된 판매자입니다.")

        return await repo.create_store_with_full_info(
            store_id=generate_store_id(),
            store_name=store_name,
            seller_email=seller_email,
            store_introduction=store_introduction,
            store_phone=store_phone,
            store_postal_code=store_postal_code,
            store_address=store_address,
            store_detail_address=store_detail_address,
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            lat=lat,
            lng=lng,
            nearest_station=nearest_station,
            walking_time=walking_time,
            sns_info=sns_info,
            operation_times=operation_times,
        )
