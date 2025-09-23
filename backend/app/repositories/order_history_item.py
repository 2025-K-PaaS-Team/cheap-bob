from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from database.mongodb_models.order_history_item import OrderHistoryItem
from repositories.mongodb_base import BaseMongoRepository


class OrderHistoryItemRepository(BaseMongoRepository[OrderHistoryItem]):
    """주문 히스토리 Repository"""
    
    def __init__(self):
        super().__init__(OrderHistoryItem)
    
    async def create_from_current_order(self, order_data: Dict[str, Any]) -> OrderHistoryItem:
        """현재 주문 데이터로부터 히스토리 생성"""
        history_item = OrderHistoryItem(
            payment_id=order_data.get("payment_id"),
            product_id=order_data.get("product_id"),
            user_id=order_data.get("user_id"),
            quantity=order_data.get("quantity"),
            price=order_data.get("price"),
            sale=order_data.get("sale"),
            total_amount=order_data.get("total_amount"),
            status=order_data.get("status", "reservation"),
            reservation_at=order_data.get("reservation_at"),
            accepted_at=order_data.get("accepted_at"),
            completed_at=order_data.get("completed_at"),
            canceled_at=order_data.get("canceled_at"),
            cancel_reason=order_data.get("cancel_reason"),
            preferred_menus=order_data.get("preferred_menus"),
            nutrition_types=order_data.get("nutrition_types"),
            allergies=order_data.get("allergies"),
            topping_types=order_data.get("topping_types")
        )
        
        return await self.create(history_item)
    
    async def bulk_archive_orders(self, orders_data: List[Dict[str, Any]]) -> int:
        """여러 주문을 일괄 아카이브"""
        history_items = []
        
        for order in orders_data:
            history_item = OrderHistoryItem(
                payment_id=order.get("payment_id"),
                product_id=order.get("product_id"),
                user_id=order.get("user_id"),
                quantity=order.get("quantity"),
                price=order.get("price"),
                sale=order.get("sale"),
                total_amount=order.get("total_amount"),
                status=order.get("status", "reservation"),
                reservation_at=order.get("reservation_at"),
                accepted_at=order.get("accepted_at"),
                completed_at=order.get("completed_at"),
                canceled_at=order.get("canceled_at"),
                cancel_reason=order.get("cancel_reason"),
                preferred_menus=order.get("preferred_menus"),
                nutrition_types=order.get("nutrition_types"),
                allergies=order.get("allergies"),
                topping_types=order.get("topping_types")
            )
            history_items.append(history_item)
        
        if history_items:
            await self.create_many(history_items)
            return len(history_items)
        return 0
    
    async def get_by_payment_id(self, payment_id: str) -> Optional[OrderHistoryItem]:
        """결제 ID로 조회"""
        return await self.get_one(payment_id=payment_id)
    
    async def get_by_product_id(self, product_id: str) -> Optional[OrderHistoryItem]:
        """상품 ID로 조회"""
        return await self.get_one(product_id=product_id)
    
    async def get_user_history(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OrderHistoryItem]:
        """사용자의 주문 히스토리 조회"""
        filters = {"user_id": user_id}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            filters["reservation_at"] = date_filter
        
        return await self.get_many(
            filters=filters,
            sort=[("reservation_at", -1)],
            limit=limit
        )
    
    async def get_store_history(
        self,
        product_ids: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OrderHistoryItem]:
        """가게의 주문 히스토리 조회 (상품 ID 목록 필요)"""
        filters = {"product_id": {"$in": product_ids}}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            filters["reservation_at"] = date_filter
        
        return await self.get_many(
            filters=filters,
            sort=[("reservation_at", -1)],
            limit=limit
        )
    
    async def get_daily_summary(self, date: datetime) -> Dict[str, Any]:
        """특정 날짜의 주문 요약 통계"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        pipeline = [
            {
                "$match": {
                    "reservation_at": {
                        "$gte": start_of_day,
                        "$lt": end_of_day
                    }
                }
            },
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$total_amount"}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_orders": {"$sum": "$count"},
                    "total_revenue": {"$sum": "$total_amount"},
                    "status_breakdown": {
                        "$push": {
                            "status": "$_id",
                            "count": "$count",
                            "amount": "$total_amount"
                        }
                    }
                }
            }
        ]
        
        result = await self.aggregate(pipeline)
        return result[0] if result else {
            "total_orders": 0,
            "total_revenue": 0,
            "status_breakdown": []
        }
    
    async def get_monthly_statistics(self, year: int, month: int) -> List[Dict[str, Any]]:
        """월별 주문 통계"""
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        
        pipeline = [
            {
                "$match": {
                    "reservation_at": {
                        "$gte": start_date,
                        "$lt": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$reservation_at"
                        }
                    },
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_order_value": {"$avg": "$total_amount"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        return await self.aggregate(pipeline)
    
    async def search_by_preferences(
        self,
        preferred_menus: Optional[List[str]] = None,
        nutrition_types: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None
    ) -> List[OrderHistoryItem]:
        """선호도 기준 검색"""
        filters = {}
        
        if preferred_menus:
            filters["preferred_menus"] = {"$regex": "|".join(preferred_menus), "$options": "i"}
        
        if nutrition_types:
            filters["nutrition_types"] = {"$regex": "|".join(nutrition_types), "$options": "i"}
            
        if allergies:
            filters["allergies"] = {"$regex": "|".join(allergies), "$options": "i"}
        
        return await self.get_many(filters=filters, limit=100)