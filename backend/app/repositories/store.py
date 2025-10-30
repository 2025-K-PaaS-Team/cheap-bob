from typing import List, Optional, Dict, Tuple
from sqlalchemy import select, and_, or_, update as sql_update, case
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.store import Store
from database.models.store_address import StoreAddress
from database.models.store_sns import StoreSNS
from database.models.store_product_info import StoreProductInfo
from database.models.store_payment_info import StorePaymentInfo
from database.models.store_operation_info import StoreOperationInfo
from database.models.customer_favorite import CustomerFavorite
from database.models.order_current_item import OrderCurrentItem
from schemas.order import OrderStatus
from repositories.base import BaseRepository


class StoreRepository(BaseRepository[Store]):
    """가게"""
    def __init__(self, session: AsyncSession):
        super().__init__(Store, session)
    
    async def get_by_store_id(self, store_id: str) -> Optional[Store]:
        """가게 ID로 조회"""
        return await self.get_by_pk(store_id)
    
    async def get_by_seller_email(self, seller_email: str) -> List[Store]:
        """판매자 이메일로 가게 목록 조회"""
        return await self.get_many(
            filters={"seller_email": seller_email},
            order_by=["-created_at"]
        )
    
    async def get_all_with_relations(self) -> List[Store]:
        """모든 가게를 관계 데이터와 함께 조회"""
        return await self.get_many(
            order_by=["-created_at"],
            load_relations=["seller", "address", "payment_info", "products", "sns_info", "images", "operation_info"]
        )
    
    async def get_with_address(self, store_id: str) -> Optional[Store]:
        """가게를 주소 정보와 함께 조회"""
        query = (
            select(Store)
            .options(selectinload(Store.address))
            .where(Store.store_id == store_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_with_full_info(self, store_id: str) -> Optional[Store]:
        """가게를 모든 관련 정보와 함께 조회"""
        query = (
            select(Store)
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.payment_info),
                selectinload(Store.seller),
                selectinload(Store.images),
                selectinload(Store.operation_info),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .where(Store.store_id == store_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_address_id(self, address_id: int) -> List[Store]:
        """주소 ID로 가게 목록 조회"""
        return await self.get_many(
            filters={"address_id": address_id},
            order_by=["store_name"],
            load_relations=["address"]
        )
    
    async def update_store_and_address_atomic(
        self,
        store_id: str,
        postal_code: str,
        address: str,
        detail_address: str,
        sido: str,
        sigungu: str,
        bname: str,
        lat: str,
        lng: str,
        nearest_station: Optional[str],
        walking_time: Optional[int]
    ) -> Store:
        """가게와 주소 정보를 업데이트"""
        
        
        # 1. 현재 가게 정보를 address와 함께 조회
        query = (
            select(Store)
            .options(selectinload(Store.address))
            .where(Store.store_id == store_id)
        )
        result = await self.session.execute(query)
        store = result.scalar_one_or_none()
        
        if not store:
            return None
        
        # 2. address_id가 있으면 주소 업데이트
        if store.address_id and all([sido, sigungu, bname, lat, lng]):
            address_update_values = {
                "sido": sido,
                "sigungu": sigungu,
                "bname": bname,
                "lat": lat,
                "lng": lng,
                "nearest_station": nearest_station,
                "walking_time": walking_time
            }
            
            await self.session.execute(
                sql_update(StoreAddress)
                .where(StoreAddress.address_id == store.address_id)
                .values(**address_update_values)
            )
        
        # 3. 가게 정보 업데이트
        store_update_values = {}
        if postal_code is not None:
            store_update_values["store_postal_code"] = postal_code
        if address is not None:
            store_update_values["store_address"] = address
        if detail_address is not None:
            store_update_values["store_detail_address"] = detail_address
        
        if store_update_values:
            await self.session.execute(
                sql_update(Store)
                .where(Store.store_id == store_id)
                .values(**store_update_values)
            )
        
        # 4. 변경사항 플러시 및 갱신된 객체 반환
        await self.session.flush()
        await self.session.refresh(store)
        
        return store
    
    async def create_store_with_full_info(
        self,
        store_id: str,
        store_name: str,
        seller_email: str,
        store_introduction: str,
        store_phone: str,
        store_postal_code: str,
        store_address: str,
        store_detail_address: str,
        # Address info
        sido: str,
        sigungu: str,
        bname: str,
        lat: str,
        lng: str,
        nearest_station: Optional[str],
        walking_time: Optional[int],
        # SNS info (optional)
        sns_info: Optional[Dict[str, Optional[str]]],
        # Operation times
        operation_times: List[Dict]
    ) -> Store:
        """가게와 모든 관련 정보를 한 번에 생성"""
        
        try:
            # 1. Address 생성
            new_address = StoreAddress(
                sido=sido,
                sigungu=sigungu,
                bname=bname,
                lat=lat,
                lng=lng,
                nearest_station=nearest_station,
                walking_time=walking_time
            )
            self.session.add(new_address)
            await self.session.flush()  # address_id 생성을 위해 flush
            
            # 2. Store 생성
            store = Store(
                store_id=store_id,
                store_name=store_name,
                seller_email=seller_email,
                store_introduction=store_introduction,
                store_phone=store_phone,
                store_postal_code=store_postal_code,
                store_address=store_address,
                store_detail_address=store_detail_address,
                address_id=new_address.address_id
            )
            self.session.add(store)
            
            # 3. SNS 정보 생성 (optional)
            if sns_info:
                sns = StoreSNS(
                    store_id=store_id,
                    instagram=sns_info.get("instagram"),
                    facebook=sns_info.get("facebook"),
                    x=sns_info.get("x"),
                    homepage=sns_info.get("homepage")
                )
                self.session.add(sns)
            
            # 4. Operation 정보 생성
            if operation_times:
                for op_time in operation_times:
                    operation = StoreOperationInfo(
                        store_id=store_id,
                        day_of_week=op_time['day_of_week'],
                        open_time=op_time['open_time'],
                        close_time=op_time['close_time'],
                        pickup_start_time=op_time['pickup_start_time'],
                        pickup_end_time=op_time['pickup_end_time'],
                        is_open_enabled=op_time['is_open_enabled'],
                        is_currently_open=False
                    )
                    self.session.add(operation)
            
            # 모든 변경사항 커밋
            await self.session.flush()
            
            # Store 객체 새로고침
            await self.session.refresh(store, ["address", "sns_info", "payment_info", "operation_info"])
            
            return store
            
        except Exception as e:
            # 트랜잭션 롤백은 상위에서 처리
            raise e
    
    async def get_stores_with_products(self) -> List[Store]:
        """상품이 있는 가게들을 모든 관련 정보와 함께 조회"""
        query = (
            select(Store)
            .join(Store.products)  # INNER JOIN으로 상품이 있는 가게만 필터링
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.created_at.desc())
            .distinct()  # 중복 제거
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def get_stores_with_products_and_favorites(self, customer_email: str, offset: int = 0, limit: int = 4) -> tuple[List[tuple[Store, bool]], bool]:
        """상품이 있는 가게들과 즐겨찾기 여부를 함께 조회"""
        
        favorite_stores_query = (
            select(CustomerFavorite.store_id)
            .where(CustomerFavorite.customer_email == customer_email)
        )
        
        query = (
            select(
                Store,
                case(
                    (Store.store_id.in_(favorite_stores_query), True),
                    else_=False
                ).label('is_favorite')
            )
            .join(Store.products)
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.created_at.desc())
            .distinct()  # 중복 제거
        )
        
        # 페이지네이션 적용
        paginated_query = query.offset(offset).limit(limit+1)
        result = await self.session.execute(paginated_query)
        items = result.unique().all()
        
        has_next = len(items) > limit
        
        return items[:limit], not has_next
    
    async def search_by_location(
        self,
        sido: str,
        sigungu: str,
        bname: str
    ) -> List[Store]:
        """위치로만 가게 검색"""
        query = (
            select(Store)
            .join(Store.address)
            .where(
                and_(
                    StoreAddress.sido == sido,
                    StoreAddress.sigungu == sigungu,
                    StoreAddress.bname == bname
                )
            )
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.store_name)
            .distinct()
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def search_by_location_with_favorites(
        self,
        sido: str,
        sigungu: str,
        bname: List[str],
        customer_email: str,
        offset: int = 0,
        limit: int = 4
    ) -> tuple[List[tuple[Store, bool]], bool]:
        """위치로 가게 검색 (즐겨찾기 정보 포함)"""
        subquery = (
            select(CustomerFavorite.store_id)
            .where(CustomerFavorite.customer_email == customer_email)
            .subquery()
        )
        
        query = (
            select(Store, Store.store_id.in_(subquery))
            .join(Store.address)
            .where(
                and_(
                    StoreAddress.sido == sido,
                    StoreAddress.sigungu == sigungu,
                    StoreAddress.bname.in_(bname)
                )
            )
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.store_name)
            .distinct()
        )
        # 페이지네이션 적용
        paginated_query = query.offset(offset).limit(limit+1)
        result = await self.session.execute(paginated_query)
        items = result.unique().all()
        
        has_next = len(items) > limit
    
        return items[:limit], not has_next
    
    async def search_by_location_and_name(
        self, 
        sido: str,
        sigungu: str, 
        bname: str,
        search_name: str
    ) -> List[Store]:
        """주소와 이름으로 가게/상품 검색"""
        query = (
            select(Store)
            .join(Store.address)
            .outerjoin(Store.products) 
            .where(
                and_(
                    StoreAddress.sido == sido,
                    StoreAddress.sigungu == sigungu,
                    StoreAddress.bname == bname,
                    or_(
                        Store.store_name.like(f"%{search_name}%"),
                        StoreProductInfo.product_name.like(f"%{search_name}%")
                    )
                )
            )
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.store_name)
            .distinct()
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def search_by_location_and_name_with_favorites(
        self, 
        sido: str,
        sigungu: str, 
        bname: List[str],
        search_name: str,
        customer_email: str,
        offset: int = 0,
        limit: int = 4
    ) -> tuple[List[tuple[Store, bool]], bool]:
        """주소와 이름으로 가게/상품 검색 (즐겨찾기 정보 포함)"""
        subquery = (
            select(CustomerFavorite.store_id)
            .where(CustomerFavorite.customer_email == customer_email)
            .subquery()
        )
        
        query = (
            select(Store, Store.store_id.in_(subquery))
            .join(Store.address)
            .outerjoin(Store.products) 
            .where(
                and_(
                    StoreAddress.sido == sido,
                    StoreAddress.sigungu == sigungu,
                    StoreAddress.bname.in_(bname),
                    or_(
                        Store.store_name.like(f"%{search_name}%"),
                        StoreProductInfo.product_name.like(f"%{search_name}%")
                    )
                )
            )
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.store_name)
            .distinct()
        )
        # 페이지네이션 적용
        paginated_query = query.offset(offset).limit(limit+1)
        result = await self.session.execute(paginated_query)
        items = result.unique().all()
        
        has_next = len(items) > limit
    
        return items[:limit], not has_next
    
    async def search_by_name(self, search_name: str) -> List[Store]:
        """이름으로 가게/상품 검색"""
        query = (
            select(Store)
            .outerjoin(Store.products)
            .where(
                or_(
                    Store.store_name.like(f"%{search_name}%"),
                    StoreProductInfo.product_name.like(f"%{search_name}%")
                )
            )
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.store_name)
            .distinct()
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def search_by_name_with_favorites(self, search_name: str, customer_email: str, offset: int = 0, limit: int = 4) -> tuple[List[tuple[Store, bool]], bool]:
        """이름으로 가게/상품 검색 (즐겨찾기 정보 포함)"""
        subquery = (
            select(CustomerFavorite.store_id)
            .where(CustomerFavorite.customer_email == customer_email)
            .subquery()
        )
        
        query = (
            select(Store, Store.store_id.in_(subquery))
            .outerjoin(Store.products)
            .where(
                or_(
                    Store.store_name.like(f"%{search_name}%"),
                    StoreProductInfo.product_name.like(f"%{search_name}%")
                )
            )
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.store_name)
            .distinct()
        )
        # 페이지네이션 적용
        paginated_query = query.offset(offset).limit(limit+1)
        result = await self.session.execute(paginated_query)
        items = result.unique().all()
        
        has_next = len(items) > limit
    
        return items[:limit], not has_next
    
    async def get_favorite_stores_with_full_info(self, customer_email: str) -> List[Store]:
        """고객이 즐겨찾기한 가게들을 모든 관련 정보와 함께 조회"""
        query = (
            select(Store)
            .join(CustomerFavorite, Store.store_id == CustomerFavorite.store_id)
            .where(CustomerFavorite.customer_email == customer_email)
            .options(
                selectinload(Store.address),
                selectinload(Store.sns_info),
                selectinload(Store.operation_info),
                selectinload(Store.images),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info)
            )
            .order_by(Store.store_name)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def has_active_orders(self, store_id: str) -> bool:
        """가게에 진행 중인 주문이 있는지 확인"""
        query = (
            select(OrderCurrentItem)
            .join(StoreProductInfo, OrderCurrentItem.product_id == StoreProductInfo.product_id)
            .where(
                and_(
                    StoreProductInfo.store_id == store_id,
                    OrderCurrentItem.status.in_([OrderStatus.reservation, OrderStatus.accept])
                )
            )
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first() is not None
