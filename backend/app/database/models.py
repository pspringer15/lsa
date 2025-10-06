from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Index, func
from .connection import Base


class SentimentPost(Base):
    __tablename__ = "sentiment_posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author = Column(String(255))
    company = Column(String(255))
    role = Column(String(255))  # Job title/role
    post_title = Column(String(500))  # Post title
    post_url = Column(String(1000))  # LinkedIn post URL
    sentiment = Column(String(50))  # 'positive', 'negative', 'neutral'
    confidence = Column(Float)
    summary = Column(Text)
    analyzed_at = Column(DateTime, server_default=func.now(), index=True)
    post_date = Column(DateTime)
    category = Column(String(50))  # 'ai_news', 'career_advice', 'new_research'

    __table_args__ = (
        Index("idx_sentiment", "sentiment"),
        Index("idx_analyzed_at", "analyzed_at"),
        Index("idx_category", "category"),
    )
