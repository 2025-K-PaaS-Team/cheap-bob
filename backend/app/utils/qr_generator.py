from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from jose import jwt
from config.settings import settings


def encode_qr_data(user_id: str, payment_id: str, product_id: str) -> Tuple[str, datetime]:
    """
    QR 데이터 인코딩
    
    Args:
        user_id: 사용자 ID
        payment_id: 결제 ID
        product_id: 상품 ID
        
    Returns:
        인코딩된 QR 데이터 문자열
    """
    created_at = datetime.now(timezone.utc)
    
    payload = {
        "user_id": user_id,
        "payment_id": payment_id,
        "product_id": product_id,
        "created_at": created_at,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5)  # 5분 유효
    }
    
    # JWT로 암호화
    encoded = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return encoded, created_at


def decode_qr_data(qr_data: str) -> Optional[Dict[str, str]]:
    """
    QR 데이터 디코딩
    
    Args:
        qr_data: 인코딩된 QR 데이터
        
    Returns:
        디코딩된 데이터 딕셔너리 또는 None (유효하지 않은 경우)
    """
    try:
        decoded = jwt.decode(qr_data, settings.SECRET_KEY, algorithms=["HS256"])
        return {
            "user_id": decoded.get("user_id"),
            "payment_id": decoded.get("payment_id"),
            "product_id": decoded.get("product_id"),
            "created_at": decoded.get("created_at")
        }
    except jwt.ExpiredSignatureError:
        return None  # 만료된 QR
    except jwt.InvalidTokenError:
        return None  # 유효하지 않은 QR


def validate_qr_data(qr_data: str, expected_user_id: str) -> tuple[bool, Optional[Dict[str, str]], Optional[str]]:
    """
    QR 데이터 검증
    
    Args:
        qr_data: QR 데이터
        expected_user_id: 예상되는 사용자 ID
        
    Returns:
        (검증 성공 여부, 디코딩된 데이터, 에러 메시지)
    """
    decoded = decode_qr_data(qr_data)
    
    if not decoded:
        return False, None, "유효하지 않거나 만료된 QR 코드입니다"
    
    if decoded["user_id"] != expected_user_id:
        return False, None, "권한이 없는 사용자입니다"
    
    return True, decoded, None