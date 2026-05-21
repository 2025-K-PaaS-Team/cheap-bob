from unittest.mock import AsyncMock


class ReservationRepositoryMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_product_id.return_value = None
        mock.create_reservation.return_value = None
        mock.delete_by_product_id.return_value = False
        mock.get_all_reservations.return_value = []
        return mock
