"""SMTP transport — 도메인 무관 클라이언트.

backend 와 동일 구현. shared 패턴 미적용 정책으로 복제.
"""
from typing import Any, Dict, Optional
import ssl
from loguru import logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import aiosmtplib

from app.config.setting import settings


class EmailSender:
    def __init__(self):
        self.smtp_host = settings.SUPER_ADMIN_SMTP_HOST
        self.smtp_port = settings.SUPER_ADMIN_SMTP_PORT
        self.smtp_user = settings.SUPER_ADMIN_SMTP_USER
        self.smtp_password = settings.SUPER_ADMIN_SMTP_PASSWORD
        self.sender_email = settings.SUPER_ADMIN_SMTP_EMAIL
        self.sender_name = settings.SUPER_ADMIN_SMTP_NAME


    def is_configured(self) -> bool:
        return bool(self.smtp_user and self.smtp_password and self.sender_email)


    async def send(
        self,
        *,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            message = self._build(
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                html_body=html_body,
            )
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                tls_context=ssl.create_default_context(),
            )
            logger.info(f"이메일 전송 성공: {recipient_email}")
            return {
                "success": True,
                "message": "이메일이 성공적으로 전송되었습니다",
                "sent_at": datetime.now(),
            }
        except aiosmtplib.SMTPAuthenticationError:
            error = "SMTP 인증 실패: Gmail 계정 또는 앱 패스워드를 확인하세요"
            logger.error(error)
            return {"success": False, "message": error, "error_type": "authentication_error"}
        except aiosmtplib.SMTPException as e:
            error = f"SMTP 에러: {e}"
            logger.error(error)
            return {"success": False, "message": error, "error_type": "smtp_error"}
        except Exception as e:
            error = f"이메일 전송 중 예외 발생: {e}"
            logger.error(error)
            return {"success": False, "message": error, "error_type": "unexpected_error"}


    def _build(
        self,
        *,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str],
    ) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["From"] = f"{self.sender_name} <{self.sender_email}>"
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))
        if html_body:
            message.attach(MIMEText(html_body, "html", "utf-8"))
        return message


email_sender = EmailSender()
