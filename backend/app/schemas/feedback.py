from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source: str = "manual"
    category: str = "general"
    department: str = "general"
    product: str = "general"
    location: str = "unknown"
    language: Optional[str] = "en"


class FeedbackOut(BaseModel):
    id: int
    user_id: int
    text: str
    language: str
    source: str
    category: str
    department: str
    product: str
    location: str
    created_at: datetime


class FeedbackUpdate(BaseModel):
    text: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    product: Optional[str] = None
    location: Optional[str] = None
