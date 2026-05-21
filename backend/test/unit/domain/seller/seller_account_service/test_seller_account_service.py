"""Tests for ``app.domain.seller.service.seller_account.SellerAccountService``.

find_or_create race-safety 중심. 그 외 메서드는 integration 이 담당.
"""
from types import SimpleNamespace
from sqlalchemy.exc import IntegrityError
import pytest


@pytest.mark.unit
class TestFindOrCreate:

    async def test_returns_existing_when_found(self, service, repo_mock):
        existing = SimpleNamespace(email="s@example.com", is_active=True)
        repo_mock.find_by_email.return_value = existing

        result = await service.find_or_create("s@example.com")

        assert result is existing
        repo_mock.save.assert_not_called()


    async def test_creates_when_missing(self, service, repo_mock):
        repo_mock.find_by_email.return_value = None

        result = await service.find_or_create("new@example.com")

        repo_mock.save.assert_awaited_once()
        assert result.email == "new@example.com"


    async def test_race_refetches_after_integrity_error(
        self, service, repo_mock, mock_session,
    ):
        winner = SimpleNamespace(email="racy@example.com", is_active=True)
        repo_mock.find_by_email.side_effect = [None, winner]
        repo_mock.save.side_effect = IntegrityError("dup", params=None, orig=None)

        result = await service.find_or_create("racy@example.com")

        assert result is winner
        mock_session.rollback.assert_awaited_once()
        assert repo_mock.find_by_email.await_count == 2


    async def test_race_reraises_when_refetch_also_missing(
        self, service, repo_mock, mock_session,
    ):
        repo_mock.find_by_email.side_effect = [None, None]
        repo_mock.save.side_effect = IntegrityError("dup", params=None, orig=None)

        with pytest.raises(IntegrityError):
            await service.find_or_create("ghost@example.com")
        mock_session.rollback.assert_awaited_once()
