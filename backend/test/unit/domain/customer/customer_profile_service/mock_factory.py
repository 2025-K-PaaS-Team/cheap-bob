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


class CustomerProfileRepoMocks:
    """detail + 4종 선호 자식 repository 의 묶음 mock."""

    def __init__(self) -> None:
        self.detail = AsyncMock()
        self.detail.find_by_customer.return_value = None
        self.preferred_menus = AsyncMock()
        self.preferred_menus.find_by_customer.return_value = []
        self.nutrition_types = AsyncMock()
        self.nutrition_types.find_by_customer.return_value = []
        self.allergies = AsyncMock()
        self.allergies.find_by_customer.return_value = []
        self.topping_types = AsyncMock()
        self.topping_types.find_by_customer.return_value = []
