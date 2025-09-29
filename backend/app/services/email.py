from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from config.settings import settings


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
    
    def send(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        이메일 전송
        
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
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"이메일 전송 성공: {recipient_email}")
            return {
                "success": True,
                "message": "이메일이 성공적으로 전송되었습니다",
                "sent_at": datetime.now()
            }
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP 인증 실패: Gmail 계정 또는 앱 패스워드를 확인하세요"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "error_type": "authentication_error"
            }
        except smtplib.SMTPException as e:
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
    
    def send_template(
        self,
        recipient_email: str,
        template_type: str = "default"
    ) -> Dict[str, Any]:
        """
        템플릿 기반 이메일 전송
        
        Args:
            recipient_email: 수신자 이메일
            template_type: 템플릿 타입 (default, welcome, order 등)
            
        Returns:
            성공 여부와 메시지를 포함한 딕셔너리
        """
        template_data = self._get_email_template(template_type, recipient_email)
        
        return self.send(
            recipient_email=recipient_email,
            subject=template_data["subject"],
            body=template_data["body"],
            html_body=template_data.get("html_body")
        )
    
    def _get_email_template(
        self,
        template_type: str,
        recipient_email: str
    ) -> Dict[str, str]:
        """이메일 템플릿 반환"""
        timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
        
        templates = {
            "default": {
                "subject": "[Cheap Bob] 테스트 이메일입니다 🍱",
                "body": self._get_default_text_template(timestamp, recipient_email),
                "html_body": self._get_default_html_template(timestamp, recipient_email)
            },
            "welcome": {
                "subject": "[Cheap Bob] 회원가입을 환영합니다! 🎉",
                "body": f"안녕하세요!\n\nCheap Bob에 가입해주셔서 감사합니다.\n이제 맛있는 도시락을 저렴하게 즐기실 수 있습니다.\n\n가입 일시: {timestamp}",
                "html_body": None
            },
            "order": {
                "subject": "[Cheap Bob] 주문이 확인되었습니다 📦",
                "body": f"주문이 정상적으로 접수되었습니다.\n\n주문 일시: {timestamp}",
                "html_body": None
            },
            "complete": {
                "subject": "[Cheap Bob] 주문이 완료되었습니다 📦",
                "body": f"주문이 정상적으로 완료되었습니다.\n\n주문 일시: {timestamp}",
                "html_body": None
            }
        }
        
        return templates.get(template_type, templates["default"])
    
    def _get_default_text_template(self, timestamp: str, recipient: str) -> str:
        """기본 텍스트 템플릿"""
        return f"""
안녕하세요!

이것은 Cheap Bob의 테스트 이메일입니다.
구글 SMTP를 사용하여 이메일이 정상적으로 발송되었습니다.

발송 시간: {timestamp}
수신자: {recipient}

이 메일은 테스트 목적으로 발송되었습니다.
© 2024 Cheap Bob. All rights reserved.
        """
    
    def _get_default_html_template(self, timestamp: str, recipient: str) -> str:
        """기본 HTML 템플릿"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; text-align: center; padding: 20px; border-radius: 10px 10px 0 0; }}
                .content {{ background-color: #f4f4f4; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍱 Cheap Bob</h1>
                </div>
                <div class="content">
                    <h2>안녕하세요!!!</h2>
                    <p>Cheap Bob 이메일 테스트 입니다.</p>
                    <p>이메일이 정상적으로 발송되었습니다.</p>
                    <p><strong>발송 시간:</strong> {timestamp}</p>
                    <p><strong>수신자:</strong> {recipient}</p>
                    <a href="#" class="button">더 알아보기</a>
                </div>
                <div class="footer">
                    <p>이 메일은 테스트 목적으로 발송되었습니다.</p>
                    <p>© 2025 Cheap Bob. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    def is_configured(self) -> bool:
        """SMTP 설정이 올바르게 구성되었는지 확인"""
        return bool(
            self.smtp_user and
            self.smtp_password and
            self.sender_email
        )

# 싱글톤 인스턴스
email_service = EmailService()