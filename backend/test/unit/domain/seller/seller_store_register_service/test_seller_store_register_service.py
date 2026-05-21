"""Tests for ``SellerStoreRegisterService``."""
from datetime import time
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import StoreAlreadyRegisteredError


def _register_kwargs():
    return dict(
        seller_email="seller@example.com",
        store_name="가게",
        store_introduction="",
        store_phone="",
        store_postal_code="",
        store_address="",
        store_detail_address="",
        sido="서울특별시", sigungu="강남구", bname="역삼동",
        lat="37.5", lng="127.0",
        nearest_station=None, walking_time=None,
        sns_info=None,
        operation_times=[{
            "day_of_week": 0,
            "open_time": time(10, 0), "close_time": time(22, 0),
            "pickup_start_time": time(11, 0), "pickup_end_time": time(21, 0),
            "is_open_enabled": True,
        }],
    )


@pytest.mark.unit
class TestRegister:

    async def test_raises_when_already_registered(self, service, store_repo_mock):
        store_repo_mock.get_by_seller_email.return_value = [SimpleNamespace()]
        with pytest.raises(StoreAlreadyRegisteredError):
            await service.register(**_register_kwargs())


    async def test_delegates_to_repo_with_generated_id(
        self, service, store_repo_mock,
    ):
        store_repo_mock.get_by_seller_email.return_value = []
        store_repo_mock.create_store_with_full_info.return_value = SimpleNamespace(
            store_id="STR_fixed",
        )

        result = await service.register(**_register_kwargs())

        assert result.store_id == "STR_fixed"
        store_repo_mock.create_store_with_full_info.assert_awaited_once()
        # 첫 키워드 인자 확인.
        call = store_repo_mock.create_store_with_full_info.await_args
        assert call.kwargs["store_id"] == "STR_fixed"
        assert call.kwargs["seller_email"] == "seller@example.com"
