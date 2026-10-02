from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int = 5


class RAGAnswer(BaseModel):
    answer: str
    sources: list[str]
    citations: list[dict]
