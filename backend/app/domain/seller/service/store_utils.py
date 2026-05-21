"""seller 도메인 내부 헬퍼.

`convert_store_to_response` 는 Store ORM 엔티티를 customer-facing 응답으로 변환하는 함수다.
customer 도메인이 store 데이터를 사용할 때 본 헬퍼를 호출한다 (schema 는 cross-domain 노출 OK,
함수는 seller 도메인의 책임이므로 여기 위치).
"""
from typing import Optional

from app.domain.seller.schema.store_settings import StoreAddressResponse
from app.domain.seller.schema.store_operation import StoreOperationResponse
from app.domain.seller.schema.store import StoreDetailResponseForCustomer, StoreSNSInfo
from app.domain.seller.schema.product import ProductResponse
from app.domain.seller.schema.image import ImageUploadResponse
from app.core.object_storage import object_storage


def convert_store_to_response(
    store, is_favorite: bool = False,
) -> StoreDetailResponseForCustomer:
    """Store ORM 엔티티 + relationships 가 모두 로드된 상태에서 customer 응답으로 변환."""
    products = [
        ProductResponse(
            product_id=p.product_id,
            store_id=p.store_id,
            product_name=p.product_name,
            description=p.description,
            initial_stock=p.initial_stock,
            current_stock=p.current_stock,
            price=p.price,
            sale=p.sale,
            version=p.version,
            nutrition_types=[
                info.nutrition_type for info in (p.nutrition_info or [])
            ],
        )
        for p in store.products
    ]

    address = StoreAddressResponse(
        store_id=store.store_id,
        postal_code=store.store_postal_code,
        address=store.store_address,
        detail_address=store.store_detail_address,
        sido=store.address.sido,
        sigungu=store.address.sigungu,
        bname=store.address.bname,
        lat=store.address.lat,
        lng=store.address.lng,
        nearest_station=store.address.nearest_station,
        walking_time=store.address.walking_time,
    )

    sns = StoreSNSInfo(
        instagram=store.sns_info.instagram if store.sns_info else None,
        facebook=store.sns_info.facebook if store.sns_info else None,
        x=store.sns_info.x if store.sns_info else None,
        homepage=store.sns_info.homepage if store.sns_info else None,
    )

    operation_times = [
        StoreOperationResponse.model_validate(op) for op in store.operation_info
    ]

    images = [
        ImageUploadResponse(
            image_id=img.image_id,
            image_url=object_storage.get_file_url(img.image_id),
            is_main=img.is_main,
            display_order=img.display_order,
        )
        for img in store.images
    ]

    return StoreDetailResponseForCustomer(
        store_id=store.store_id,
        store_name=store.store_name,
        store_introduction=store.store_introduction,
        store_phone=store.store_phone,
        seller_email=store.seller_email,
        created_at=store.created_at,
        address=address,
        sns=sns,
        operation_times=operation_times,
        images=images,
        products=products,
        is_favorite=is_favorite,
    )


def get_main_image_url(store) -> Optional[str]:
    """대표 이미지 URL."""
    if not store.images:
        return None
    for image in store.images:
        if image.is_main:
            return object_storage.get_file_url(image.image_id)
    return None
