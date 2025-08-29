### 테스트 데이터    
    
from typing import Dict

fake_stores_products: Dict[int, Dict] = {
    "test": {
        "store_name": "cake_store",
        "products": [
            {"product_id": "cake1", "product_name": "치즈 케이크", "stock": 10, "price": 8000},
            {"product_id": "cake2", "product_name": "리얼 치즈 케이크", "stock": 15, "price": 8000},
            {"product_id": "cake3", "product_name": "리얼 파이널 치즈 케이크", "stock": 20, "price": 9000},
        ]
    }
}

fake_payments: Dict[str, Dict] = {}

fake_portone_config = {
    "portone_channel_id": "channel-key-2bde6533-669f-4e5a-ae0c-5a471f10a463",
    "portone_store_id": "store-f7494ada-17a2-49c9-bb23-183d354afb27"
}