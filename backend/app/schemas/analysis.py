from pydantic import BaseModel
from typing import List, Optional


class Solution(BaseModel):
    title: str
    explanation: str
    code: str
    confidence: float
    source_urls: Optional[List[str]] = []


class AnalysisResponse(BaseModel):
    # Parsed error info
    error_type: Optional[str]
    error_message: Optional[str]
    language: str
    file_path: Optional[str]
    line_number: Optional[int]

    # LLM analysis
    root_cause: str
    reasoning: str
    solutions: List[Solution]

    # Metadata
    sources_used: int
    analysis_id: Optional[int] = None
