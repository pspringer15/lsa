from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    content: str
    author: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    post_title: Optional[str] = None
    post_url: Optional[str] = None
    post_date: Optional[datetime] = None
    category: Optional[str] = None


class SentimentResult(BaseModel):
    sentiment: str  # positive | negative | neutral
    confidence: float
    summary: str


class SentimentPostCreate(PostBase, SentimentResult):
    pass


class SentimentPostResponse(PostBase, SentimentResult):
    id: int
    analyzed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AnalyzeResponse(BaseModel):
    added: int
    processed: int
    skipped: int
    message: Optional[str] = None


class TrendDistribution(BaseModel):
    sentiment: str
    count: int


class TrendItem(BaseModel):
    date: str
    positive: int = 0
    neutral: int = 0
    negative: int = 0


class TrendsResponse(BaseModel):
    timeline: List[TrendItem]
    distribution: List[TrendDistribution]
    insights: Dict[str, str]
