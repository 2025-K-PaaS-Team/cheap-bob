from typing import List
from pydantic import BaseModel


class SearchHistoryResponse(BaseModel):
    search_names: List[str]
    count: int
