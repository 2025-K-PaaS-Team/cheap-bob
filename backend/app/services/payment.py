from datetime import datetime
from typing import Dict, List, Optional
import random

from examples.products import fake_stores_products, fake_payments, fake_portone_config
from core.portone import PortOneClient
from utils.id_generator import generate_payment_id

class PaymentService:
    """
    결제 관련 비즈니스 로직을 처리하는 서비스 클래스
    """
    
    @staticmethod
    async def create_payment_session(product_id: str, quantity: int, customer_email: Optional[str] = None) -> Dict:
        """
        결제 세션을 생성하고 포트원 결제 정보를 반환합니다.
        """
        # 상품 정보 찾기
        product_info = None
        store_id = None
        
        for sid, store_data in fake_stores_products.items():
            for product in store_data["products"]:
                if product["product_id"] == product_id:
                    product_info = product
                    store_id = sid
                    break
            if product_info:
                break
        
        if not product_info:
            return {
                "success": False,
                "error": "상품을 찾을 수 없습니다."
            }
        
        # 재고 확인
        if product_info["stock"] < quantity:
            return {
                "success": False,
                "error": f"재고가 부족합니다. 현재 재고: {product_info['stock']}개"
            }
        
        # 결제 ID 생성
        payment_id = generate_payment_id()
        total_amount = product_info["price"] * quantity
        
        # 결제 정보 저장
        fake_payments[payment_id] = {
            "payment_id": payment_id,
            "product_id": product_id,
            "product_name": product_info["product_name"],
            "store_id": store_id,
            "quantity": quantity,
            "unit_price": product_info["price"],
            "total_amount": total_amount,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        return {
            "success": True,
            "payment_id": payment_id,
            "total_amount": total_amount,
            "portone_config": fake_portone_config
        }
    
    @staticmethod
    async def verify_payment(payment_id: str, customer_email: Optional[str] = None) -> Dict:
        """
        포트원에서 결제를 검증하고 결제 상태를 업데이트합니다.
        """
        if payment_id not in fake_payments:
            return {
                "success": False,
                "error": "결제 정보를 찾을 수 없습니다."
            }
        
        actual_payment = PortOneClient.get_payment(payment_id)
        details = PortOneClient.extract_payment_details(actual_payment)
            
        return {
            "success": True
        }
        
    @staticmethod
    async def process_refund(payment_id: str, reason: str = "고객 요청", customer_email: Optional[str] = None) -> Dict:
        """
        결제를 환불 처리합니다.
        """
        
        # 포트원 환불 요청
        refund_result = PortOneClient.cancel_payment(
            payment_id=payment_id,
            reason=reason
        )
        
        return refund_result