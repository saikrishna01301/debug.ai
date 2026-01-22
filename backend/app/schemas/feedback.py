from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeedbackRequest(BaseModel):
    analysis_id: int
    solution_index: int  # Which solution they tried (0, 1, or 2)
    worked: bool
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    analysis_id: int
    solution_index: int
    worked: bool
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
