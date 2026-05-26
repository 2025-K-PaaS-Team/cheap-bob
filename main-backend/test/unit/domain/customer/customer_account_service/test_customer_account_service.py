"""Tests for ``app.domain.customer.service.customer_account.CustomerAccountService``.

find_or_create 의 race-safety 가 핵심 검증 대상. is_active / set_active / hard_delete 는
integration test 가 실제 DB 행위까지 커버하므로 단위 테스트에서는 race 분기에 집중.
"""
from types import SimpleNamespace
from sqlalchemy.exc import IntegrityError
import pytest


@pytest.mark.unit
class TestFindOrCreate:

    async def test_returns_existing_when_found(self, service, repo_mock):
        existing = SimpleNamespace(email="a@example.com", is_active=True)
        repo_mock.find_by_email.return_value = existing

        result = await service.find_or_create("a@example.com")

        assert result is existing
        repo_mock.save.assert_not_called()


    async def test_creates_when_missing(self, service, repo_mock):
        repo_mock.find_by_email.return_value = None

        result = await service.find_or_create("new@example.com")

        repo_mock.save.assert_awaited_once()
        # repo mock 의 save side_effect 가 입력 그대로 반환 → Customer 인스턴스.
        assert result.email == "new@example.com"


    async def test_race_refetches_after_integrity_error(
        self, service, repo_mock, mock_session,
    ):
        """동시 OAuth 콜백 race: 우리 find 는 None, save 도중 IntegrityError, 재조회 시 winner row 발견."""
        winner = SimpleNamespace(email="racy@example.com", is_active=True)
        # find: 처음엔 None, IntegrityError 후 재조회에선 winner.
        repo_mock.find_by_email.side_effect = [None, winner]
        repo_mock.save.side_effect = IntegrityError("dup", params=None, orig=None)

        result = await service.find_or_create("racy@example.com")

        assert result is winner
        # rollback 으로 세션을 정리한 뒤 다시 query 했는지.
        mock_session.rollback.assert_awaited_once()
        assert repo_mock.find_by_email.await_count == 2


    async def test_race_reraises_when_refetch_also_missing(
        self, service, repo_mock, mock_session,
    ):
        """진짜 비정상: IntegrityError 가 났는데 재조회에서도 row 가 없다면 그대로 raise."""
        repo_mock.find_by_email.side_effect = [None, None]
        repo_mock.save.side_effect = IntegrityError("dup", params=None, orig=None)

        with pytest.raises(IntegrityError):
            await service.find_or_create("ghost@example.com")
        mock_session.rollback.assert_awaited_once()
