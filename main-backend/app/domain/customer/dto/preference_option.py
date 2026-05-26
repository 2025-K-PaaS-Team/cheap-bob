from dataclasses import dataclass


@dataclass(frozen=True)
class PreferenceOption:
    """프론트 셀렉터 옵션 — type=백엔드 식별값, name=사용자 노출명(한국어)."""
    type: str
    name: str
