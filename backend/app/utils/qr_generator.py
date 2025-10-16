from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from jose import jwt
from config.settings import settings


def encode_qr_data(customer_id: str, payment_id: str, product_id: str) -> Tuple[str, datetime]:
    """
    QR 데이터 인코딩
    
    Args:
        customer_id: 사용자 ID
        payment_id: 결제 ID
        product_id: 상품 ID
        
    Returns:
        인코딩된 QR 데이터 문자열
    """
    now = datetime.now(timezone.utc)
    
    payload = {
        "customer_id": customer_id,
        "payment_id": payment_id,
        "product_id": product_id,
        "iat": now,
        "exp": now + timedelta(minutes=5)
    }
    
    # JWT로 암호화
    encoded = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return encoded, now


def decode_qr_data(qr_data: str) -> Optional[Dict[str, str]]:
    """
    QR 데이터 디코딩
    
    Args:
        qr_data: 인코딩된 QR 데이터
        
    Returns:
        디코딩된 데이터 딕셔너리 또는 None (유효하지 않은 경우)
    """
    try:
        decoded = jwt.decode(qr_data, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        return {
            "customer_id": decoded.get("customer_id"),
            "payment_id": decoded.get("payment_id"),
            "product_id": decoded.get("product_id"),
            "created_at": decoded.get("iat")
        }
    except jwt.ExpiredSignatureError:
        return None  # 만료된 QR
    except jwt.InvalidTokenError:
        return None  # 유효하지 않은 QR


def validate_qr_data(qr_data: str, expected_customer_id: str) -> tuple[bool, Optional[Dict[str, str]], Optional[str]]:
    """
    QR 데이터 검증
    
    Args:
        qr_data: QR 데이터
        expected_customer_id: 예상되는 소비자 ID
        
    Returns:
        (검증 성공 여부, 디코딩된 데이터, 에러 메시지)
    """
    decoded = decode_qr_data(qr_data)
    
    if not decoded:
        return False, None, "유효하지 않거나 만료된 QR 코드입니다"
    
    if decoded["customer_id"] != expected_customer_id:
        return False, None, "권한이 없는 소비자입니다"
    
    return True, decoded, None