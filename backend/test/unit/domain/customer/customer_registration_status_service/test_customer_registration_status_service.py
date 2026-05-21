"""Tests for ``CustomerRegistrationStatusService``."""
import pytest


@pytest.mark.unit
class TestGetStatus:

    async def test_returns_profile_when_no_detail(self, service, detail_repo_mock):
        detail_repo_mock.exists_by_customer.return_value = False
        assert await service.get_status("alice@example.com") == "profile"


    async def test_returns_complete_when_detail_exists(self, service, detail_repo_mock):
        detail_repo_mock.exists_by_customer.return_value = True
        assert await service.get_status("alice@example.com") == "complete"
