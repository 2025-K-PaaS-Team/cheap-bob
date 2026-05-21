"""Tests for ``app.util.image_validator.validate_image_files``.

검증 대상:
  - magic bytes 일치 → 통과
  - declared content_type vs detected format 불일치 → 400
  - magic bytes 가 알 수 없는 시그니처 → 400
  - 미지원 content_type → 400
  - 크기 초과 → 413
"""
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, UploadFile
import pytest


_JPEG_MAGIC = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
_WEBP_MAGIC = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
_BOGUS = b"<html>not an image</html>" + b"\x00" * 100


def _fake_upload(*, filename: str, content_type: str, content: bytes) -> MagicMock:
    """UploadFile 의 minimal mock — read/seek 만 사용."""
    fake = MagicMock(spec=UploadFile)
    fake.filename = filename
    fake.content_type = content_type
    fake.file = BytesIO(content)
    fake.read = AsyncMock(return_value=content)
    fake.seek = AsyncMock(return_value=None)
    return fake


@pytest.mark.unit
class TestValidateImageFiles:

    async def test_valid_jpeg_passes(self):
        from app.util.image_validator import validate_image_files

        f = _fake_upload(filename="x.jpg", content_type="image/jpeg", content=_JPEG_MAGIC)
        result = await validate_image_files([f])
        assert len(result) == 1


    async def test_valid_png_passes(self):
        from app.util.image_validator import validate_image_files

        f = _fake_upload(filename="x.png", content_type="image/png", content=_PNG_MAGIC)
        result = await validate_image_files([f])
        assert len(result) == 1


    async def test_valid_webp_passes(self):
        from app.util.image_validator import validate_image_files

        f = _fake_upload(filename="x.webp", content_type="image/webp", content=_WEBP_MAGIC)
        result = await validate_image_files([f])
        assert len(result) == 1


    async def test_image_jpg_alias_normalized_to_image_jpeg(self):
        """``image/jpg`` 는 비표준 MIME 이지만 JPEG 와 같은 포맷으로 본다."""
        from app.util.image_validator import validate_image_files

        f = _fake_upload(filename="x.jpg", content_type="image/jpg", content=_JPEG_MAGIC)
        result = await validate_image_files([f])
        assert len(result) == 1


    async def test_unsupported_content_type_raises_400(self):
        from app.util.image_validator import validate_image_files

        f = _fake_upload(filename="x.gif", content_type="image/gif", content=b"GIF89a" + b"\x00" * 100)
        with pytest.raises(HTTPException) as exc:
            await validate_image_files([f])
        assert exc.value.status_code == 400


    async def test_magic_bytes_spoofing_blocked(self):
        """헤더는 image/jpeg 이지만 실제 내용은 HTML — 위조 시도 차단."""
        from app.util.image_validator import validate_image_files

        f = _fake_upload(filename="evil.jpg", content_type="image/jpeg", content=_BOGUS)
        with pytest.raises(HTTPException) as exc:
            await validate_image_files([f])
        assert exc.value.status_code == 400


    async def test_cross_format_spoofing_blocked(self):
        """헤더는 image/png 인데 실제는 JPEG magic bytes — declared 와 detected 불일치."""
        from app.util.image_validator import validate_image_files

        f = _fake_upload(filename="x.png", content_type="image/png", content=_JPEG_MAGIC)
        with pytest.raises(HTTPException) as exc:
            await validate_image_files([f])
        assert exc.value.status_code == 400


    async def test_size_limit_raises_413(self):
        from app.util.image_validator import validate_image_files

        # 15 MB + 1 byte
        oversized = _PNG_MAGIC + b"\x00" * (15 * 1024 * 1024)
        f = _fake_upload(filename="big.png", content_type="image/png", content=oversized)
        with pytest.raises(HTTPException) as exc:
            await validate_image_files([f])
        assert exc.value.status_code == 413
