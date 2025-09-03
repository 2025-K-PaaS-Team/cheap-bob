from datetime import datetime
from typing import Dict, List, Optional
import random

from core.portone import PortOneClient
from utils.id_generator import generate_payment_id

class PaymentService:
    """
    결제 관련 비즈니스 로직을 처리하는 서비스 클래스
    """
    
    @staticmethod
    async def verify_payment(payment_id: str, secret_key: str) -> Dict:
        """
        포트원에서 결제를 검증하고 결제 상태를 업데이트합니다.
        """

        # 가게별 secret key를 사용하여 PortOneClient 생성
        portone_client = PortOneClient(secret_key=secret_key)
        actual_payment = portone_client.get_payment(payment_id)
        details = PortOneClient.extract_payment_details(actual_payment)
            
        return {
            "success": True,
            "payment_info": details
        }
        
    @staticmethod
    async def process_refund(payment_id: str, secret_key: str, reason: str) -> Dict:
        """
        결제를 환불 처리합니다.
        """
        
        # 가게별 secret key를 사용하여 PortOneClient 생성
        portone_client = PortOneClient(secret_key=secret_key)
        
        # 포트원 환불 요청
        refund_result = portone_client.cancel_payment(
            payment_id=payment_id,
            reason=reason
        )
        
        refund_result["success"] = True
        return refund_result