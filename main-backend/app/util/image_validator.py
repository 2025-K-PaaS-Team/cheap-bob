"""이미지 업로드 검증 — content_type + size + magic bytes 시그니처.

content_type 만 검사하면 클라이언트가 헤더만 위조해도 통과되어 비-이미지 파일을
업로드할 수 있다 (XSS payload 가 담긴 HTML, 실행 파일 등). magic bytes 검증으로
실제 파일 시그니처가 헤더와 일치하는지 확인해 차단.

지원 포맷의 magic bytes:
  - JPEG : ``\\xff\\xd8\\xff`` (3 bytes, 첫 SOI marker)
  - PNG  : ``\\x89PNG\\r\\n\\x1a\\n`` (8 bytes, 표준 시그니처)
  - WEBP : ``RIFF????WEBP`` (12 bytes — 0-3 'RIFF', 8-11 'WEBP')
"""
from typing import List, Tuple
from fastapi import HTTPException, UploadFile, status


_MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
_ALLOWED_TYPES = frozenset({"image/jpeg", "image/jpg", "image/png", "image/webp"})


def _detect_image_format(content: bytes) -> str | None:
    """magic bytes 로 실제 이미지 포맷 추정. 알 수 없으면 None."""
    if len(content) >= 3 and content[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if len(content) >= 8 and content[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if (
        len(content) >= 12
        and content[:4] == b"RIFF"
        and content[8:12] == b"WEBP"
    ):
        return "image/webp"
    return None


def _content_type_matches_format(declared: str, detected: str) -> bool:
    """``image/jpg`` 와 ``image/jpeg`` 는 같은 포맷으로 본다."""
    normalize = lambda mt: "image/jpeg" if mt == "image/jpg" else mt
    return normalize(declared) == normalize(detected)


async def validate_image_files(
    files: List[UploadFile],
) -> List[Tuple[object, str, str]]:
    """업로드된 이미지 파일들을 검증해 (file_obj, filename, content_type) 튜플 리스트 반환.

    검증 단계:
      1) content_type 이 허용 목록에 있는지
      2) 파일 크기가 ``_MAX_FILE_SIZE`` 이하인지
      3) magic bytes 가 실제 이미지 시그니처와 일치하는지 + declared content_type 과 같은지

    Raises:
        HTTPException 400 — 형식 불일치 / magic bytes 실패
        HTTPException 413 — 파일 크기 초과
    """
    validated = []
    for f in files:
        if f.content_type not in _ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 형식입니다: {f.filename}",
            )
        content = await f.read()
        if len(content) > _MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"파일 크기가 너무 큽니다 (최대 15MB): {f.filename}",
            )
        detected = _detect_image_format(content)
        if detected is None or not _content_type_matches_format(
            f.content_type, detected,
        ):
            # 헤더는 image/* 이지만 실제 magic bytes 가 비-이미지 — 위조 시도 또는 손상 파일.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"파일이 손상되었거나 유효한 이미지가 아닙니다: {f.filename}",
            )
        await f.seek(0)
        validated.append((f.file, f.filename, f.content_type))
    return validated
