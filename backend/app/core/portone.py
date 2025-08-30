import json
import portone_server_sdk as portone
from config.settings import settings
from fastapi import HTTPException
from typing import Any

class PortOneClient:

    client = portone.PaymentClient(secret=settings.test_portone_v2_api_secret)

    @classmethod
    def get_payment(cls, payment_id: str) -> portone.payment.PaidPayment:
        try:
            payment = cls.client.get_payment(payment_id=payment_id)
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
    
    @classmethod
    def extract_payment_details(cls, payment: portone.payment.PaidPayment) -> dict:
 
        # 금액 정보
        amount = payment.amount.paid if payment.amount else 0

        # 상품 이름
        good_name = getattr(payment, 'order_name', None)
        
        # 결제 수단 정보
        payment_method = "카카오페이" 
        if hasattr(payment, 'method') and payment.method:
            if hasattr(payment.method, 'type'):
                payment_method = payment.method.type
            if hasattr(payment.method, 'easy_pay') and payment.method.easy_pay:
                if hasattr(payment.method.easy_pay, 'provider'):
                    payment_method = f"{payment.method.easy_pay.provider}"
        
        return {
            "amount": amount,
            "good_name": good_name,
            "payment_method": payment_method
        }
    
    @classmethod
    def cancel_payment(cls, payment_id: str, reason: str = "고객 요청") -> dict:
        try:

            # 환불
            result = cls.client.cancel_payment(
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
