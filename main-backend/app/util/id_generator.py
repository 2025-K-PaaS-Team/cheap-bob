import uuid
from datetime import datetime


def generate_store_id() -> str:
    """가게 고유 ID 생성"""
    timestamp = int(datetime.now().timestamp())
    unique_part = uuid.uuid4().hex[:8]
    return f"STR_{timestamp}_{unique_part}"


def generate_product_id() -> str:
    """상품 고유 ID 생성"""
    timestamp = int(datetime.now().timestamp())
    unique_part = uuid.uuid4().hex[:8]
    return f"PRD_{timestamp}_{unique_part}"


def generate_payment_id() -> str:
    """결제 고유 ID 생성"""
    timestamp = int(datetime.now().timestamp())
    unique_part = uuid.uuid4().hex[:8]
    return f"PAY_{unique_part}_{timestamp}"