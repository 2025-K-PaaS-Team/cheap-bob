"""이메일 인프라.

- `sender` — SMTP transport (`EmailSender`, `email_sender` singleton)
- `notifier` — 도메인 이벤트별 dispatch 함수 (도메인 자산 의존 X)
- `template/` — HTML 본문 생성 함수
"""
from app.core.email.sender import EmailSender, email_sender


__all__ = ["EmailSender", "email_sender"]
