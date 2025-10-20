import json
import portone_server_sdk as portone
from config.settings import settings
from fastapi import HTTPException
from typing import Any, Optional

class PortOneClient:
    """
    PortOne API 클라이언트
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        secret_key가 제공되지 않으면 기본 테스트 키 사용
        """
        self.secret = secret_key
        self.client = portone.PaymentClient(secret=self.secret)

    def get_payment(self, payment_id: str) -> portone.payment.PaidPayment:
        try:
            payment = self.client.get_payment(payment_id=payment_id)
            if not isinstance(payment, portone.payment.PaidPayment):
                raise ValueError(f"유효하지 않은 결제 정보입니다. Type: {type(payment)}")
            return payment
        
        except portone.payment.GetPaymentError as e:
            raise HTTPException(
                status_code=400, detail=f"결제 정보를 가져올 수 없습니다: {str(e)}"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"예상치 못한 오류: {str(e)}"
            )
    
    @staticmethod
    def extract_payment_details(payment: portone.payment.PaidPayment) -> dict:
 
        # 금액 정보
        amount = payment.amount

        # 상품 이름
        good_name = payment.order_name
        
        # 결제 수단 정보
        payment_method = payment.method
        
        return {
            "amount": amount,
            "good_name": good_name,
            "payment_method": payment_method
        }
    
    def cancel_payment(self, payment_id: str, reason: str = "고객 요청") -> dict:
        try:

            # 환불
            result = self.client.cancel_payment(
                payment_id=payment_id,
                reason=reason
            )
            
            if hasattr(result, '__dict__'):
                return result.__dict__
            else:
                return {"status": "success", "payment_id": payment_id}
                
        except portone.payment.CancelPaymentError as e:
            raise HTTPException(
                status_code=400, detail=f"환불 처리 중 오류가 발생했습니다: {str(e)}"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"예상치 못한 오류: {str(e)}"
            )
