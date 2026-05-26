"""Tests for ``app.domain.order.service.qr`` 의 인코딩/디코딩/검증.

QR 은 JWT 기반이라 stateless — UoW / repository 없이 함수만 검증한다.
"""
from unittest.mock import patch
import pytest
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.domain.order.service.qr import (
    decode_qr_data,
    encode_qr_data,
    validate_qr_data,
)
from app.config.setting import settings


pytestmark = pytest.mark.unit


class TestEncodeDecodeRoundTrip:

    def test_round_trip_preserves_payload(self):
        token, _ = encode_qr_data("alice@example.com", "PAY_x", "PRD_x")

        decoded = decode_qr_data(token)
        assert decoded is not None
        assert decoded["customer_id"] == "alice@example.com"
        assert decoded["payment_id"] == "PAY_x"
        assert decoded["product_id"] == "PRD_x"


    def test_expired_token_returns_none(self):
        # exp 가 과거인 JWT 직접 생성.
        past = datetime.now(timezone.utc) - timedelta(minutes=5)
        token = jwt.encode(
            {
                "customer_id": "alice@example.com",
                "payment_id": "PAY_x",
                "product_id": "PRD_x",
                "iat": past,
                "exp": past + timedelta(seconds=10),
            },
            settings.JWT_SECRET, settings.JWT_ALGORITHM,
        )
        assert decode_qr_data(token) is None


    def test_invalid_token_returns_none(self):
        assert decode_qr_data("not-a-jwt") is None


class TestValidate:

    def test_returns_error_when_invalid(self):
        ok, decoded, error = validate_qr_data(
            "not-a-jwt", expected_customer_id="alice@example.com",
        )
        assert ok is False
        assert decoded is None
        assert "유효하지" in error


    def test_returns_error_when_customer_mismatch(self):
        token, _ = encode_qr_data("alice@example.com", "PAY_x", "PRD_x")
        ok, _, error = validate_qr_data(token, expected_customer_id="other@example.com")
        assert ok is False
        assert "권한" in error


    def test_returns_ok_for_matching_customer(self):
        token, _ = encode_qr_data("alice@example.com", "PAY_x", "PRD_x")
        ok, decoded, error = validate_qr_data(
            token, expected_customer_id="alice@example.com",
        )
        assert ok is True
        assert decoded["payment_id"] == "PAY_x"
        assert error is None
