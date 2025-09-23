from typing import Generic, Optional, Type, TypeVar, List, Dict, Any
from beanie import Document
from pymongo.errors import DuplicateKeyError
from datetime import datetime


DocumentType = TypeVar("DocumentType", bound=Document)


class BaseMongoRepository(Generic[DocumentType]):
    """MongoDB Base Repository with generic CRUD operations"""
    
    def __init__(self, model: Type[DocumentType]):
        self.model = model
    
    async def create(self, document: DocumentType) -> DocumentType:
        """새 문서 생성"""
        try:
            await document.insert()
            return document
        except DuplicateKeyError:
            raise ValueError(f"Document with the same key already exists")
    
    async def create_many(self, documents: List[DocumentType]) -> List[DocumentType]:
        """여러 문서 일괄 생성"""
        result = await self.model.insert_many(documents)
        return documents
    
    async def get_by_id(self, document_id: str) -> Optional[DocumentType]:
        """ID로 문서 조회"""
        return await self.model.get(document_id)
    
    async def get_one(self, **filters) -> Optional[DocumentType]:
        """필터 조건으로 단일 문서 조회"""
        return await self.model.find_one(filters)
    
    async def get_many(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[DocumentType]:
        """필터, 정렬, 페이지네이션을 지원하는 다중 문서 조회"""
        query = self.model.find(filters or {})
        
        if sort:
            query = query.sort(sort)
        
        if skip:
            query = query.skip(skip)
            
        if limit:
            query = query.limit(limit)
        
        return await query.to_list()
    
    async def count(self, **filters) -> int:
        """조건에 맞는 문서 수 조회"""
        return await self.model.find(filters).count()
    
    async def update(self, document: DocumentType) -> DocumentType:
        """문서 업데이트"""
        await document.save()
        return document
    
    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """조건에 맞는 첫 번째 문서 업데이트"""
        result = await self.model.find_one(filter_dict).update({"$set": update_dict})
        return result is not None
    
    async def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        """조건에 맞는 모든 문서 업데이트"""
        result = await self.model.find(filter_dict).update_many({"$set": update_dict})
        return result.modified_count if result else 0
    
    async def delete(self, document: DocumentType) -> bool:
        """문서 삭제"""
        result = await document.delete()
        return result is not None
    
    async def delete_by_id(self, document_id: str) -> bool:
        """ID로 문서 삭제"""
        document = await self.get_by_id(document_id)
        if document:
            return await self.delete(document)
        return False
    
    async def delete_many(self, **filters) -> int:
        """조건에 맞는 여러 문서 삭제"""
        result = await self.model.find(filters).delete()
        return result.deleted_count if result else 0
    
    async def exists(self, **filters) -> bool:
        """조건에 맞는 문서 존재 여부 확인"""
        count = await self.count(**filters)
        return count > 0
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """MongoDB aggregation pipeline 실행"""
        return await self.model.aggregate(pipeline).to_list(length=None)
    
    async def find_with_text_search(self, search_text: str, limit: int = 10) -> List[DocumentType]:
        """텍스트 검색 (text index 필요)"""
        return await self.model.find(
            {"$text": {"$search": search_text}}
        ).limit(limit).to_list()
    
    async def find_by_date_range(
        self,
        field: str,
        start_date: datetime,
        end_date: datetime,
        **additional_filters
    ) -> List[DocumentType]:
        """날짜 범위로 조회"""
        filters = {
            field: {
                "$gte": start_date,
                "$lte": end_date
            },
            **additional_filters
        }
        return await self.model.find(filters).to_list()
    
    async def bulk_upsert(self, documents: List[DocumentType], key_fields: List[str]) -> int:
        """일괄 upsert (존재하면 업데이트, 없으면 생성)"""
        updated_count = 0
        
        for doc in documents:
            # key_fields를 기준으로 필터 생성
            filter_dict = {field: getattr(doc, field) for field in key_fields if hasattr(doc, field)}
            
            existing = await self.model.find_one(filter_dict)
            if existing:
                # 업데이트
                update_dict = doc.model_dump(exclude={"id", "_id"})
                await existing.update({"$set": update_dict})
                updated_count += 1
            else:
                # 새로 생성
                await doc.insert()
                updated_count += 1
                
        return updated_count