from unittest.mock import AsyncMock


class StorePaymentInfoServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.register.return_value = None
        mock.exists_by_store.return_value = False
        mock.find_by_store.return_value = None
        mock.update_portone_ids.return_value = None
        return mock
