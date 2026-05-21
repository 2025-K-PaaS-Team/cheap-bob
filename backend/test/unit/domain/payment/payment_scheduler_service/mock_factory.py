from unittest.mock import AsyncMock, MagicMock


class APSchedulerMockFactory:
    """APScheduler.add_job / get_job / remove_job 흉내 — 동기 메서드."""

    @classmethod
    def create(cls) -> MagicMock:
        mock = MagicMock(name="apscheduler")
        mock.add_job = MagicMock(return_value=None)
        mock.get_job = MagicMock(return_value=None)
        mock.remove_job = MagicMock(return_value=None)
        return mock


class SellerProductServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.restore_purchased_stock.return_value = None
        return mock


class OrderQueryServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.delete_cart_item.return_value = True
        return mock
