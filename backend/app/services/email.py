from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import ssl
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from config.settings import settings
from services.email_templates import reservation, accept, customer_cancel, seller_cancel

class EmailService:
    """구글 SMTP를 사용한 이메일 전송 서비스"""
    
    def __init__(self):
        self.smtp_host = settings.SUPER_ADMIN_SMTP_HOST
        self.smtp_port = settings.SUPER_ADMIN_SMTP_PORT
        self.smtp_user = settings.SUPER_ADMIN_SMTP_USER
        self.smtp_password = settings.SUPER_ADMIN_SMTP_PASSWORD
        self.sender_email = settings.SUPER_ADMIN_SMTP_EMAIL
        self.sender_name = settings.SUPER_ADMIN_SMTP_NAME
    
    def _create_message(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> MIMEMultipart:
        """이메일 메시지 객체 생성"""
        message = MIMEMultipart("alternative")
        message["From"] = f"{self.sender_name} <{self.sender_email}>"
        message["To"] = recipient_email
        message["Subject"] = subject
        
        text_part = MIMEText(body, "plain", "utf-8")
        message.attach(text_part)
        
        if html_body:
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)
        
        return message
    
    async def send(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        비동기 이메일 전송
        
        Args:
            recipient_email: 수신자 이메일
            subject: 이메일 제목
            body: 이메일 본문 (텍스트)
            html_body: 이메일 본문 (HTML, 선택사항)
            
        Returns:
            성공 여부와 메시지를 포함한 딕셔너리
        """
        try:
            message = self._create_message(
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                html_body=html_body
            )
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
                tls_context=ssl.create_default_context()
            )
            
            logger.info(f"이메일 전송 성공: {recipient_email}")
            return {
                "success": True,
                "message": "이메일이 성공적으로 전송되었습니다",
                "sent_at": datetime.now()
            }
            
        except aiosmtplib.SMTPAuthenticationError:
            error_msg = "SMTP 인증 실패: Gmail 계정 또는 앱 패스워드를 확인하세요"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "error_type": "authentication_error"
            }
        except aiosmtplib.SMTPException as e:
            error_msg = f"SMTP 에러: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "error_type": "smtp_error"
            }
        except Exception as e:
            error_msg = f"이메일 전송 중 예외 발생: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "error_type": "unexpected_error"
            }
    
    async def send_template(
        self,
        recipient_email: str,
        store_name: str,
        template_type: str
    ) -> Dict[str, Any]:
        """
        템플릿 기반 비동기 이메일 전송
        
        Args:
            recipient_email: 수신자 이메일
            template_type: 템플릿 타입
            store_name: 가게 이름
            
        Returns:
            성공 여부와 메시지를 포함한 딕셔너리
        """
        template_data = self._get_email_template(template_type, recipient_email, store_name)
        
        return await self.send(
            recipient_email=recipient_email,
            subject=template_data["subject"],
            body=template_data["body"],
            html_body=template_data.get("html_body")
        )
    
    def _get_email_template(
        self,
        template_type: str,
        recipient_email: str,
        store_name: str
    ) -> Dict[str, str]:
        """이메일 템플릿 반환"""
        timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
        
        templates = {
            "reservation": {
                "subject": "[저렴한끼] 🎉 주문이 등록되었습니다!",
                "body": reservation.get_reservation_text_template(timestamp, recipient_email),
                "html_body": reservation.get_reservation_html_template(timestamp, recipient_email)
            },
            "accept": {
                "subject": "[저렴한끼] 🎉 픽업이 확정되었습니다!",
                "body": accept.get_accept_text_template(timestamp, recipient_email, store_name),
                "html_body": accept.get_accept_html_template(timestamp, recipient_email, store_name)
            },
            "customer_cancel": {
                "subject": "[저렴한끼] 주문이 취소되었습니다.",
                "body": customer_cancel.get_customer_cancel_text_template(timestamp, recipient_email, store_name),
                "html_body": customer_cancel.get_cusotmer_cancel_html_template(timestamp, recipient_email, store_name)
            },
            "seller_cancel": {
                "subject": "[저렴한끼] 가게가 주문을 취소하였습니다.",
                "body": seller_cancel.get_seller_cancel_text_template(timestamp, recipient_email, store_name),
                "html_body": seller_cancel.get_seller_cancel_html_template(timestamp, recipient_email, store_name)
            }
        }
        
        return templates.get(template_type)

    def is_configured(self) -> bool:
        """SMTP 설정이 올바르게 구성되었는지 확인"""
        return bool(
            self.smtp_user and
            self.smtp_password and
            self.sender_email
        )

# 싱글톤 인스턴스
email_service = EmailService()