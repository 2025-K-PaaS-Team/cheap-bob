from unittest.mock import AsyncMock, MagicMock


class FakeUnitOfWork:
    def __init__(self, session):
        self._session = session


    async def __aenter__(self):
        return self._session


    async def __aexit__(self, exc_type, exc, tb):
        return False


def make_mock_session() -> MagicMock:
    session = MagicMock(name="session")
    session.flush = AsyncMock()
    return session


class StoreImageRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = []
        mock.get_by_pk.return_value = None
        mock.create_initial_images.return_value = []
        mock.set_as_main.return_value = None
        mock.delete_image.return_value = True
        mock.get_main_images_for_stores.return_value = {}
        return mock


class StoreRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = None
        return mock


class ObjectStorageMockFactory:
    @classmethod
    def create(cls) -> MagicMock:
        # 동기 + 비동기 메서드가 섞여 있어 MagicMock + AsyncMock 으로 wiring.
        mock = MagicMock()
        mock.upload_multiple_files = AsyncMock(return_value=[])
        mock.delete_file = AsyncMock(return_value=True)
        mock.get_file_url = MagicMock(side_effect=lambda key: f"http://s3/{key}")
        return mock
