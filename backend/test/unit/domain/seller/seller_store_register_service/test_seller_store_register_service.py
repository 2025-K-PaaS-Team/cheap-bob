"""Tests for ``SellerStoreRegisterService``."""
from types import SimpleNamespace
import pytest
from datetime import time

from app.domain.seller.service.exception import StoreAlreadyRegisteredError


def _register_kwargs(*, sns_info=None):
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
        sns_info=sns_info,
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


    async def test_creates_store_via_sub_repos_with_generated_id(
        self,
        service,
        store_repo_mock,
        address_repo_mock,
        sns_repo_mock,
        operation_repo_mock,
    ):
        store_repo_mock.get_by_seller_email.return_value = []
        address_repo_mock.create.return_value = SimpleNamespace(address_id=42)
        store_repo_mock.create.return_value = SimpleNamespace(store_id="STR_fixed")

        result = await service.register(
            **_register_kwargs(sns_info={"instagram": "https://ig/x"}),
        )

        assert result.store_id == "STR_fixed"
        address_repo_mock.create.assert_awaited_once()
        store_repo_mock.create.assert_awaited_once()
        # 생성된 address_id 가 store INSERT 의 FK 로 들어갔는지.
        assert store_repo_mock.create.await_args.kwargs["address_id"] == 42
        assert store_repo_mock.create.await_args.kwargs["store_id"] == "STR_fixed"
        sns_repo_mock.create.assert_awaited_once()
        operation_repo_mock.create_initial_operation_info.assert_awaited_once()


    async def test_skips_sns_when_omitted(
        self,
        service,
        store_repo_mock,
        address_repo_mock,
        sns_repo_mock,
        operation_repo_mock,
    ):
        store_repo_mock.get_by_seller_email.return_value = []

        await service.register(**_register_kwargs(sns_info=None))

        sns_repo_mock.create.assert_not_awaited()
        operation_repo_mock.create_initial_operation_info.assert_awaited_once()
