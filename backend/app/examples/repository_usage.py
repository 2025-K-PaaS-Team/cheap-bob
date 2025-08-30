"""
개선된 Repository 사용 예시
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from repositories import (
    StoreRepository,
    StoreProductInfoRepository,
    CartItemRepository,
    OrderCurrentItemRepository
)


# 1. 기본 CRUD 작업
async def basic_crud_example(db: AsyncSession):
    store_repo = StoreRepository(db)
    
    # 생성
    new_store = await store_repo.create(
        store_id="STORE001",
        store_name="맛있는 밥집",
        seller_email="seller@example.com"
    )
    
    # Primary Key로 조회
    store = await store_repo.get_by_pk("STORE001")
    
    # 필터로 조회
    stores = await store_repo.get_many(
        filters={"seller_email": "seller@example.com"}
    )
    
    # 업데이트
    updated_store = await store_repo.update(
        "STORE001",
        store_name="더 맛있는 밥집"
    )
    
    # 삭제
    deleted = await store_repo.delete("STORE001")


# 2. 고급 필터링 예시
async def advanced_filtering_example(db: AsyncSession):
    product_repo = StoreProductInfoRepository(db)
    
    # 가격 범위로 필터링
    products = await product_repo.get_many(
        filters={
            "price": {"gte": 5000, "lte": 10000},
            "current_stock": {"gt": 0}
        }
    )
    
    # 이름으로 검색
    search_results = await product_repo.get_many(
        filters={"product_name": {"like": "김치"}},
        order_by=["product_name"]
    )
    
    # 여러 값 중 하나
    products_in_stores = await product_repo.get_many(
        filters={"store_id": ["STORE001", "STORE002", "STORE003"]}
    )


# 3. 관계 데이터 로딩
async def relationship_loading_example(db: AsyncSession):
    store_repo = StoreRepository(db)
    
    # 관계 데이터와 함께 조회
    stores = await store_repo.get_many(
        load_relations=["seller", "products", "location"]
    )
    
    # 이제 N+1 쿼리 없이 관계 데이터 접근 가능
    for store in stores:
        print(f"Store: {store.store_name}")
        print(f"Seller: {store.seller.email}")
        print(f"Products: {len(store.products)}")


# 4. 페이지네이션
async def pagination_example(db: AsyncSession):
    product_repo = StoreProductInfoRepository(db)
    
    # 페이지 1: 처음 10개
    page1 = await product_repo.get_many(
        limit=10,
        offset=0,
        order_by=["-created_at"]
    )
    
    # 페이지 2: 다음 10개
    page2 = await product_repo.get_many(
        limit=10,
        offset=10,
        order_by=["-created_at"]
    )
    
    # 전체 개수 확인
    total_count = await product_repo.count()


# 5. 복잡한 비즈니스 로직
async def business_logic_example(db: AsyncSession):
    cart_repo = CartItemRepository(db)
    product_repo = StoreProductInfoRepository(db)
    order_repo = OrderCurrentItemRepository(db)
    
    # 장바구니에서 주문으로 이동
    user_id = "USER001"
    cart_items = await cart_repo.get_by_user_id(user_id)
    
    for cart_item in cart_items:
        # 재고 확인 및 차감 (낙관적 락 사용)
        product = await product_repo.decrease_stock(
            cart_item.product_id,
            cart_item.quantity
        )
        
        if product:
            # 주문 생성
            order = await order_repo.create(
                payment_id=cart_item.payment_id,
                product_id=cart_item.product_id,
                store_id=product.store_id,
                user_id=user_id,
                quantity=cart_item.quantity,
                price=cart_item.price,
                is_complete=False
            )
            
            # 장바구니에서 삭제
            await cart_repo.delete(cart_item.payment_id)
        else:
            # 재고 부족 처리
            print(f"재고 부족: {cart_item.product_id}")


# 6. 통계 및 집계
async def statistics_example(db: AsyncSession):
    order_repo = OrderCurrentItemRepository(db)
    store_id = "STORE001"
    
    # Repository의 커스텀 메서드 사용
    stats = await order_repo.get_store_order_stats(store_id)
    
    print(f"총 주문 수: {stats['total_orders']}")
    print(f"완료된 주문: {stats['completed_orders']}")
    print(f"대기 중 주문: {stats['pending_orders']}")
    print(f"총 매출: {stats['total_sales']:,}원")


# 7. 배치 작업
async def batch_operation_example(db: AsyncSession):
    cart_repo = CartItemRepository(db)
    product_repo = StoreProductInfoRepository(db)
    
    # 만료된 장바구니 항목 정리
    expired_items = await cart_repo.get_expired_items(expire_minutes=30)
    
    for item in expired_items:
        # 재고 복원
        await product_repo.restore_stock(item.product_id, item.quantity)
        # 장바구니에서 삭제
        await cart_repo.delete(item.payment_id)
    
    # 특정 조건의 상품 일괄 업데이트
    # 재고가 10개 미만인 상품에 20% 세일 적용
    low_stock_products = await product_repo.get_many(
        filters={"current_stock": {"lt": 10}}
    )
    
    for product in low_stock_products:
        await product_repo.update(product.product_id, sale=20)