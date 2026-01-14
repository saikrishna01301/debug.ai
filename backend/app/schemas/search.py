from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    query: str
    limit: int = 3

class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    tags: List[str]
    votes: int
    distance: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int