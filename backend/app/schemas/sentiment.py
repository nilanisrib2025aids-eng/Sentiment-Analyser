from typing import Literal, Optional

from pydantic import BaseModel, Field


class SentimentAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source: str = "manual"
    category: Optional[str] = "general"
    department: Optional[str] = "general"
    product: Optional[str] = "general"
    location: Optional[str] = "unknown"
    language: Optional[str] = "en"


class SentimentBatchRequest(BaseModel):
    items: list[SentimentAnalyzeRequest]


class SentimentPrediction(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0, le=1)
    positive_score: float = Field(ge=0, le=1)
    negative_score: float = Field(ge=0, le=1)
    neutral_score: float = Field(ge=0, le=1)
    language: str
    explanation: str
    important_keywords: list[str]
