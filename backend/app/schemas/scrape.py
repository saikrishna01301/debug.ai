from pydantic import BaseModel, Field
from typing import Optional


class ScrapeRequest(BaseModel):
    tag: str = Field(
        ...,
        description="Stack Overflow tag to scrape (e.g., 'python', 'javascript', 'react')",
    )
    limit: int = Field(
        default=100, ge=1, le=1000, description="Number of posts to scrape (1-1000)"
    )

    class Config:
        json_schema_extra = {"example": {"tag": "python", "limit": 500}}


class ScrapeResponse(BaseModel):
    status: str
    message: str
    tag: str
    posts_scraped: Optional[int] = None
    error: Optional[str] = None
