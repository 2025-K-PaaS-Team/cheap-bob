"""Tests for ``app.domain.seller.service.seller_store_settings.SellerStoreSettingsService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import (
    StoreNotFoundError,
    StoreOperationReservationNotFoundError,
)


@pytest.mark.unit
class TestUpdateAddress:

    async def test_raises_when_store_missing(self, service, store_repo_mock):
        store_repo_mock.get_with_address.return_value = None
        with pytest.raises(StoreNotFoundError):
            await service.update_address(
                store_id="STR_x",
                postal_code="", address="", detail_address="",
                sido="", sigungu="", bname="",
                lat="0", lng="0",
                nearest_station=None, walking_time=None,
            )


    async def test_updates_both_address_and_store_columns(
        self, service, store_repo_mock, address_repo_mock,
    ):
        store_repo_mock.get_with_address.return_value = SimpleNamespace(
            store_id="STR_x", address_id=42,
        )

        result = await service.update_address(
            store_id="STR_x",
            postal_code="06236", address="강남구", detail_address="101호",
            sido="서울", sigungu="강남구", bname="역삼동",
            lat="37.5", lng="127.0",
            nearest_station=None, walking_time=None,
        )
        assert result.store_id == "STR_x"
        address_repo_mock.update.assert_awaited_once()
        # address_id (FK 값) 가 첫 인자, 주소 필드들이 kwargs.
        assert address_repo_mock.update.await_args.args[0] == 42
        assert address_repo_mock.update.await_args.kwargs["sido"] == "서울"
        store_repo_mock.update.assert_awaited_once_with(
            "STR_x",
            store_postal_code="06236",
            store_address="강남구",
            store_detail_address="101호",
        )


    async def test_skips_address_update_when_legacy_store_has_no_address_id(
        self, service, store_repo_mock, address_repo_mock,
    ):
        store_repo_mock.get_with_address.return_value = SimpleNamespace(
            store_id="STR_legacy", address_id=None,
        )

        await service.update_address(
            store_id="STR_legacy",
            postal_code="", address="", detail_address="",
            sido="", sigungu="", bname="",
            lat="0", lng="0",
            nearest_station=None, walking_time=None,
        )
        address_repo_mock.update.assert_not_awaited()
        store_repo_mock.update.assert_awaited_once()


@pytest.mark.unit
class TestUpsertOperationModifications:

    async def test_creates_when_absent(self, service, modification_repo_mock):
        modification_repo_mock.get_by_store_id.return_value = []

        await service.upsert_operation_modifications(
            store_id="STR_x", modifications=[],
        )
        modification_repo_mock.create_modifications_batch.assert_awaited_once()
        modification_repo_mock.update_modifications_batch.assert_not_awaited()


    async def test_updates_when_present(self, service, modification_repo_mock):
        modification_repo_mock.get_by_store_id.return_value = [SimpleNamespace()]

        await service.upsert_operation_modifications(
            store_id="STR_x", modifications=[],
        )
        modification_repo_mock.update_modifications_batch.assert_awaited_once()
        modification_repo_mock.create_modifications_batch.assert_not_awaited()


@pytest.mark.unit
class TestDeleteOperationModifications:

    async def test_raises_when_missing(self, service, modification_repo_mock):
        modification_repo_mock.delete_all_by_store_id.side_effect = ValueError("none")
        with pytest.raises(StoreOperationReservationNotFoundError):
            await service.delete_operation_modifications("STR_x")


    async def test_happy_path(self, service, modification_repo_mock):
        modification_repo_mock.delete_all_by_store_id.return_value = 3
        # 정상 종료.
        await service.delete_operation_modifications("STR_x")
        modification_repo_mock.delete_all_by_store_id.assert_awaited_once_with("STR_x")


@pytest.mark.unit
class TestApplyPendingModifications:

    async def test_returns_zero_when_empty(self, service, modification_repo_mock):
        modification_repo_mock.get_all_with_operation_info.return_value = []
        assert await service.apply_pending_modifications() == (0, 0)


    async def test_applies_each_mod_then_deletes(
        self, service, modification_repo_mock, operation_repo_mock,
    ):
        from datetime import time

        modification_repo_mock.get_all_with_operation_info.return_value = [
            SimpleNamespace(
                modification_id=1, operation_id=10,
                new_open_time=time(9, 0),
                new_close_time=time(21, 0),
                new_pickup_start_time=None,
                new_pickup_end_time=None,
                new_is_open_enabled=None,
                operation_info=SimpleNamespace(store_id="STR_x", day_of_week=0),
            ),
        ]

        applied, failed = await service.apply_pending_modifications()
        assert applied == 1
        assert failed == 0
        operation_repo_mock.apply_modification.assert_awaited_once()
        modification_repo_mock.delete_by_modification_id.assert_awaited_once_with(1)


    async def test_per_item_error_swallowed(
        self, service, modification_repo_mock, operation_repo_mock,
    ):
        from datetime import time
        modification_repo_mock.get_all_with_operation_info.return_value = [
            SimpleNamespace(
                modification_id=1, operation_id=10,
                new_open_time=time(9, 0),
                new_close_time=time(21, 0),
                new_pickup_start_time=None,
                new_pickup_end_time=None,
                new_is_open_enabled=None,
                operation_info=SimpleNamespace(store_id="STR_x", day_of_week=0),
            ),
        ]
        operation_repo_mock.apply_modification.side_effect = RuntimeError("boom")

        applied, failed = await service.apply_pending_modifications()
        assert applied == 0
        assert failed == 1


@pytest.mark.unit
class TestUpdateTodayOpenStatus:

    async def test_skips_stores_without_payment_info(
        self, service, operation_repo_mock, payment_info_mock,
    ):
        operation_repo_mock.get_by_day_of_week.return_value = [
            SimpleNamespace(store_id="STR_a"),
            SimpleNamespace(store_id="STR_b"),
        ]
        payment_info_mock.has_complete_info.side_effect = [True, False]
        operation_repo_mock.update_today_open_status_for_stores.return_value = 1

        updated, skipped = await service.update_today_open_status()
        assert updated == 1
        assert skipped == 1
        # STR_a 만 update 대상으로 전달됐는지.
        called_ids = operation_repo_mock.update_today_open_status_for_stores.await_args.args[0]
        assert called_ids == ["STR_a"]
