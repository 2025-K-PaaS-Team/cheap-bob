from typing import Dict, Any
from loguru import logger
from services.email import email_service


async def send_reservation_email(customer_email: str) -> Dict[str, Any]:
    """예약 확인 이메일 백그라운드 전송"""
    try:
        if not email_service.is_configured():
            logger.warning("이메일 서비스가 설정되지 않음")
            return {"success": False, "message": "Email service not configured"}
        
        result = await email_service.send_template(
            recipient_email=customer_email,
            store_name="",
            template_type="reservation"
        )
        
        if not result["success"]:
            logger.error(f"예약 이메일 전송 실패: {customer_email} - {result['message']}")
        
        return result
    except Exception as e:
        logger.error(f"예약 이메일 백그라운드 전송 중 오류: {str(e)}")
        return {"success": False, "message": str(e)}


async def send_order_accepted_email(customer_email: str, store_name: str) -> Dict[str, Any]:
    """주문 확정 이메일 백그라운드 전송"""
    try:
        if not email_service.is_configured():
            logger.warning("이메일 서비스가 설정되지 않음")
            return {"success": False, "message": "Email service not configured"}
        
        result = await email_service.send_template(
            recipient_email=customer_email,
            store_name=store_name,
            template_type="accept"
        )
        
        if not result["success"]:
            logger.error(f"주문 확정 이메일 전송 실패: {customer_email} - {result['message']}")
        
        return result
    except Exception as e:
        logger.error(f"주문 확정 이메일 백그라운드 전송 중 오류: {str(e)}")
        return {"success": False, "message": str(e)}


async def send_customer_cancel_email(customer_email: str, store_name: str) -> Dict[str, Any]:
    """고객 주문 취소 이메일 백그라운드 전송"""
    try:
        if not email_service.is_configured():
            logger.warning("이메일 서비스가 설정되지 않음")
            return {"success": False, "message": "Email service not configured"}
        
        result = await email_service.send_template(
            recipient_email=customer_email,
            store_name=store_name,
            template_type="customer_cancel"
        )
        
        if not result["success"]:
            logger.error(f"고객 취소 이메일 전송 실패: {customer_email} - {result['message']}")
        
        return result
    except Exception as e:
        logger.error(f"고객 취소 이메일 백그라운드 전송 중 오류: {str(e)}")
        return {"success": False, "message": str(e)}


async def send_seller_cancel_email(customer_email: str, store_name: str) -> Dict[str, Any]:
    """가게 주문 취소 이메일 백그라운드 전송"""
    try:
        if not email_service.is_configured():
            logger.warning("이메일 서비스가 설정되지 않음")
            return {"success": False, "message": "Email service not configured"}
        
        result = await email_service.send_template(
            recipient_email=customer_email,
            store_name=store_name,
            template_type="seller_cancel"
        )
        
        if not result["success"]:
            logger.error(f"가게 취소 이메일 전송 실패: {customer_email} - {result['message']}")
        
        return result
    except Exception as e:
        logger.error(f"가게 취소 이메일 백그라운드 전송 중 오류: {str(e)}")
        return {"success": False, "message": str(e)}