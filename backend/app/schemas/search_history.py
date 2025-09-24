from pydantic import BaseModel
from typing import List


class SearchHistoryResponse(BaseModel):
    """검색 히스토리 응답 모델"""
    search_names: List[str]
    count: int