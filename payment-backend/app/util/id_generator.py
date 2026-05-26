import uuid
from datetime import datetime


def generate_payment_id() -> str:
    """결제 고유 ID 생성"""
    timestamp = int(datetime.now().timestamp())
    unique_part = uuid.uuid4().hex[:8]
    return f"PAY_{unique_part}_{timestamp}"
