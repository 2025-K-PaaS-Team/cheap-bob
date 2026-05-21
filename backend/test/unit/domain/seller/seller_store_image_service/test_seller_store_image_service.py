"""Tests for ``app.domain.seller.service.seller_store_image.SellerStoreImageService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import (
    StoreImageDuplicateError,
    StoreImageMainDeleteError,
    StoreImageNotFoundError,
    StoreNotFoundError,
)


def _store(seller_email: str = "owner@example.com") -> SimpleNamespace:
    return SimpleNamespace(store_id="STR_x", seller_email=seller_email)


@pytest.mark.unit
class TestInitImages:

    async def test_store_missing_raises(self, service, store_repo_mock):
        store_repo_mock.get_by_store_id.return_value = None
        with pytest.raises(StoreNotFoundError):
            await service.init_images(
                store_id="STR_x", seller_email="owner@example.com", files=[],
            )


    async def test_other_owner_raises(self, service, store_repo_mock):
        store_repo_mock.get_by_store_id.return_value = _store(seller_email="other@example.com")
        with pytest.raises(StoreImageNotFoundError):
            await service.init_images(
                store_id="STR_x", seller_email="owner@example.com", files=[],
            )


    async def test_duplicate_existing_images_raises(
        self, service, store_repo_mock, image_repo_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_store_id.return_value = [SimpleNamespace()]
        with pytest.raises(StoreImageDuplicateError):
            await service.init_images(
                store_id="STR_x", seller_email="owner@example.com", files=[],
            )


    async def test_upload_empty_raises(
        self, service, store_repo_mock, image_repo_mock, object_storage_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_store_id.return_value = []
        object_storage_mock.upload_multiple_files.return_value = []  # 업로드 실패
        with pytest.raises(StoreImageNotFoundError):
            await service.init_images(
                store_id="STR_x", seller_email="owner@example.com",
                files=[(object(), "a.jpg", "image/jpeg")],
            )


    async def test_happy_path_creates_initial_images(
        self, service, store_repo_mock, image_repo_mock, object_storage_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_store_id.return_value = []
        object_storage_mock.upload_multiple_files.return_value = [
            ("main_key", "http://s3/main.jpg"),
            ("other_key", "http://s3/other.jpg"),
        ]
        image_repo_mock.create_initial_images.return_value = [
            SimpleNamespace(image_id="main_key", is_main=True, display_order=0),
            SimpleNamespace(image_id="other_key", is_main=False, display_order=1),
        ]

        result = await service.init_images(
            store_id="STR_x", seller_email="owner@example.com",
            files=[
                (object(), "a.jpg", "image/jpeg"),
                (object(), "b.jpg", "image/jpeg"),
            ],
        )

        assert result.total == 2
        image_repo_mock.create_initial_images.assert_awaited_once_with(
            store_id="STR_x", main_image_id="main_key", other_image_ids=["other_key"],
        )


@pytest.mark.unit
class TestDeleteImage:

    async def test_other_owner_raises(self, service, store_repo_mock):
        store_repo_mock.get_by_store_id.return_value = _store(
            seller_email="other@example.com",
        )
        with pytest.raises(StoreImageNotFoundError):
            await service.delete_image(
                store_id="STR_x", seller_email="owner@example.com",
                image_id="img_x",
            )


    async def test_main_image_delete_raises(
        self, service, store_repo_mock, image_repo_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_pk.return_value = SimpleNamespace(
            image_id="img_x", store_id="STR_x", is_main=True,
        )
        with pytest.raises(StoreImageMainDeleteError):
            await service.delete_image(
                store_id="STR_x", seller_email="owner@example.com",
                image_id="img_x",
            )


    async def test_image_missing_raises(
        self, service, store_repo_mock, image_repo_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_pk.return_value = None
        with pytest.raises(StoreImageNotFoundError):
            await service.delete_image(
                store_id="STR_x", seller_email="owner@example.com",
                image_id="img_x",
            )


    async def test_deletes_s3_and_db(
        self, service, store_repo_mock, image_repo_mock, object_storage_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_pk.return_value = SimpleNamespace(
            image_id="img_x", store_id="STR_x", is_main=False,
        )

        assert await service.delete_image(
            store_id="STR_x", seller_email="owner@example.com",
            image_id="img_x",
        ) is True
        object_storage_mock.delete_file.assert_awaited_once_with("img_x")
        image_repo_mock.delete_image.assert_awaited_once_with("img_x")


@pytest.mark.unit
class TestChangeMainImage:

    async def test_other_owner_raises(self, service, store_repo_mock):
        store_repo_mock.get_by_store_id.return_value = _store(
            seller_email="other@example.com",
        )
        with pytest.raises(StoreImageNotFoundError):
            await service.change_main_image(
                store_id="STR_x", seller_email="owner@example.com",
                new_main_image_id="img_x",
            )


    async def test_target_image_missing_raises(
        self, service, store_repo_mock, image_repo_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_pk.return_value = None
        with pytest.raises(StoreImageNotFoundError):
            await service.change_main_image(
                store_id="STR_x", seller_email="owner@example.com",
                new_main_image_id="img_x",
            )


    async def test_swaps_main(
        self, service, store_repo_mock, image_repo_mock,
    ):
        store_repo_mock.get_by_store_id.return_value = _store()
        image_repo_mock.get_by_pk.return_value = SimpleNamespace(
            image_id="img_x", store_id="STR_x", is_main=False,
        )
        image_repo_mock.set_as_main.return_value = SimpleNamespace(
            image_id="img_x", is_main=True, display_order=1,
        )

        result = await service.change_main_image(
            store_id="STR_x", seller_email="owner@example.com",
            new_main_image_id="img_x",
        )

        assert result.is_main is True
        image_repo_mock.set_as_main.assert_awaited_once_with("img_x")
