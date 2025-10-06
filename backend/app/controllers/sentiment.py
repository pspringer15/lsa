from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from typing import List

from fastapi import APIRouter
from sqlalchemy import select, func

from app.database.connection import SessionLocal
from app.database.models import SentimentPost
from app.models.schemas import (
    SentimentPostResponse,
    AnalyzeResponse,
    TrendsResponse,
    TrendItem,
    TrendDistribution,
)
from app.services.scraper import generate_mock_posts, fetch_posts_by_category
from app.services.analyzer import analyze_posts

router = APIRouter(prefix="/api", tags=["sentiment"])


def _is_low_quality_post(summary: str, confidence: float, sentiment: str) -> bool:
    """Filter out image-only posts and posts without real opinions."""
    summary_lower = summary.lower()
    
    # Skip image/video/document posts without substance
    if any(phrase in summary_lower for phrase in [
        "image post; sentiment not explicit",
        "video post; sentiment not explicit",
        "document about",
        "article about",
        "poll about"
    ]):
        return True
    
    # Skip very short generic summaries
    if len(summary) < 30 and sentiment == "neutral" and confidence < 0.65:
        return True
    
    return False


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(category: str = "ai_news") -> AnalyzeResponse:
    """Analyze LinkedIn posts by category.
    
    Args:
        category: One of 'ai_news', 'career_advice', 'new_research' (default: 'ai_news')
    """
    posts = fetch_posts_by_category(category=category, max_posts=50)
    analyses = analyze_posts(posts)

    added = 0
    skipped = 0
    with SessionLocal() as session:
        for post, res in zip(posts, analyses):
            # Skip low-quality posts (images, videos, no real opinion)
            if _is_low_quality_post(res["summary"], res["confidence"], res["sentiment"]):
                skipped += 1
                continue
            
            # dedupe by content + post_date
            exists = session.execute(
                select(SentimentPost.id).where(
                    SentimentPost.content == post["content"],
                    SentimentPost.post_date == post.get("post_date"),
                )
            ).first()
            if exists:
                skipped += 1
                continue
            row = SentimentPost(
                content=post["content"],
                author=post.get("author"),
                company=post.get("company"),
                role=post.get("role"),
                post_title=post.get("post_title"),
                post_url=post.get("post_url"),
                sentiment=res["sentiment"],
                confidence=res["confidence"],
                summary=res["summary"],
                post_date=post.get("post_date"),
                analyzed_at=datetime.utcnow(),
                category=post.get("category"),
            )
            session.add(row)
            added += 1
        session.commit()

    return AnalyzeResponse(added=added, processed=len(posts), skipped=skipped, message="Analysis complete")


@router.get("/posts", response_model=List[SentimentPostResponse])
async def get_posts(limit: int = 50, category: str = None) -> List[SentimentPostResponse]:
    """Get posts, optionally filtered by category.
    
    Args:
        limit: Maximum number of posts to return (default: 50)
        category: Filter by category ('ai_news', 'career_advice', 'new_research')
    """
    with SessionLocal() as session:
        query = select(SentimentPost).order_by(SentimentPost.analyzed_at.desc())
        
        if category:
            query = query.where(SentimentPost.category == category)
        
        rows = session.execute(query.limit(limit)).scalars().all()
        return rows


@router.get("/trends", response_model=TrendsResponse)
async def get_trends() -> TrendsResponse:
    with SessionLocal() as session:
        d_col = func.date(SentimentPost.post_date).label("d")
        rows = session.execute(
            select(
                d_col,
                SentimentPost.sentiment,
                func.count().label("c"),
            ).group_by(d_col, SentimentPost.sentiment).order_by(d_col)
        ).all()

        # timeline aggregation
        timeline_map = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
        for d, s, c in rows:
            s = s or "neutral"
            if s not in timeline_map[d]:
                timeline_map[d][s] = 0
            timeline_map[d][s] += int(c)

        timeline: List[TrendItem] = []
        for d in sorted(timeline_map.keys()):
            counts = timeline_map[d]
            timeline.append(TrendItem(
                date=str(d),
                positive=counts.get("positive", 0),
                neutral=counts.get("neutral", 0),
                negative=counts.get("negative", 0),
            ))

        # distribution
        dist_rows = session.execute(
            select(SentimentPost.sentiment, func.count()).group_by(SentimentPost.sentiment)
        ).all()
        distribution = [
            TrendDistribution(sentiment=(s or "neutral"), count=int(c)) for s, c in dist_rows
        ]

    insights = {
        "bestCodingModel": "GPT-5 High-Reasoning leads with 88% developer satisfaction",
        "businessTrend": "45% of Fortune 500 now using AI for customer service",
        "coolUseCase": "AI-powered drone swarms for disaster relief coordination",
    }

    return TrendsResponse(timeline=timeline, distribution=distribution, insights=insights)
