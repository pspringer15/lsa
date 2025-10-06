from __future__ import annotations
import json
import re
from typing import List, Dict
import logging

from app.config import settings
from app.config_models import get_openai_model

logger = logging.getLogger(__name__)


def _heuristic_sentiment(text: str) -> Dict:
    """Fallback heuristic-based sentiment analysis when OpenAI is unavailable."""
    t = text.lower()
    positive_kw = ["game-changing", "up ", "increase", "improved", "gains", "love", "amazing", "great", "caught", "future is here", "promising"]
    negative_kw = ["warning", "hallucinates", "down ", "regression", "risk", "issue", "bug", "slow", "caution"]

    score = 0
    for kw in positive_kw:
        if kw in t:
            score += 1
    for kw in negative_kw:
        if kw in t:
            score -= 1

    if score > 0:
        sentiment = "positive"
        confidence = min(0.9, 0.6 + 0.1 * score)
    elif score < 0:
        sentiment = "negative"
        confidence = min(0.9, 0.6 + 0.1 * abs(score))
    else:
        sentiment = "neutral"
        confidence = 0.55

    summary = text[:180] + ("…" if len(text) > 180 else "")
    return {"sentiment": sentiment, "confidence": round(confidence, 2), "summary": summary}


def _try_parse_json(s: str):
    """Attempt to parse JSON from OpenAI response, handling various formats."""
    try:
        return json.loads(s)
    except Exception:
        # attempt to extract json block from markdown code blocks or other wrapping
        m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", s, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        # try to find raw JSON array
        m = re.search(r"(\[.*\])", s, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        return None


def _analyze_with_openai(posts: List[Dict]) -> List[Dict]:
    """Use OpenAI for semantic sentiment extraction."""
    from openai import OpenAI
    
    logger.info(f"Starting OpenAI analysis for {len(posts)} posts")

    client = OpenAI(api_key=settings.openai_api_key)
    
    # Prepare items with IDs for tracking
    items = [{"id": i, "content": p["content"][:500]} for i, p in enumerate(posts)]  # Limit content length
    logger.debug(f"Prepared {len(items)} items for analysis")
    
    # Enhanced prompt for better semantic understanding
    system_prompt = """You are an expert sentiment analysis system specializing in AI/LLM industry news and social media posts.

Your task is to analyze LinkedIn posts about AI developments and determine:
1. Sentiment: positive, negative, or neutral
2. Confidence: a score between 0 and 1 indicating how confident you are
3. Summary: a detailed summary (30-50 words) capturing the author's main opinion, key points, and perspective

Consider:
- Technical achievements and breakthroughs → positive
- Concerns, warnings, or limitations → negative
- Factual reporting without strong opinion → neutral
- Sarcasm and irony in context

For the summary, focus on what the author actually thinks and says, not just facts. Include their perspective and reasoning.

Respond ONLY with a valid JSON object containing an "analyses" array. No markdown, no explanations."""

    user_prompt = f"""Analyze these LinkedIn posts about AI/LLM news:

{json.dumps(items, indent=2)}

Return a JSON object with this exact structure:
{{
  "analyses": [
    {{"id": 0, "sentiment": "positive", "confidence": 0.85, "summary": "30-50 word detailed summary of author's opinion and key points"}},
    {{"id": 1, "sentiment": "negative", "confidence": 0.72, "summary": "30-50 word detailed summary of author's opinion and key points"}}
  ]
}}"""

    logger.debug(f"System prompt length: {len(system_prompt)} chars")
    logger.debug(f"User prompt length: {len(user_prompt)} chars")
    logger.debug(f"First post content: {posts[0]['content'][:100]}..." if posts else "No posts")

    try:
        model_name = get_openai_model()
        logger.info(f"Calling OpenAI API with model: {model_name}")
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        logger.info(f"OpenAI API call successful. Status: {resp.model}, Usage: {resp.usage}")
        
        content = resp.choices[0].message.content or "{}"
        logger.info(f"Raw OpenAI response length: {len(content)} chars")
        logger.debug(f"Full OpenAI response: {content}")
        
        # Parse the response
        try:
            parsed = json.loads(content)
            logger.info(f"Successfully parsed JSON. Type: {type(parsed)}, Keys: {parsed.keys() if isinstance(parsed, dict) else 'N/A'}")
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing failed: {je}")
            logger.error(f"Problematic content: {content[:500]}")
            raise
        
        # Handle both array and object with array wrapper
        if isinstance(parsed, dict) and "analyses" in parsed:
            data = parsed["analyses"]
            logger.info(f"Found 'analyses' key with {len(data)} items")
        elif isinstance(parsed, dict) and "results" in parsed:
            data = parsed["results"]
            logger.info(f"Found 'results' key with {len(data)} items")
        elif isinstance(parsed, list):
            data = parsed
            logger.info(f"Response is a list with {len(data)} items")
        else:
            logger.warning(f"Unexpected response structure: {list(parsed.keys()) if isinstance(parsed, dict) else type(parsed)}")
            # Try to find any array in the response
            data = _try_parse_json(content) or []
            logger.info(f"Fallback parsing found {len(data)} items")
        
        if not data:
            logger.error("No data extracted from OpenAI response!")
            logger.error(f"Parsed object: {parsed}")
            raise ValueError("No analysis data found in OpenAI response")
        
        # Map results by ID to preserve order
        by_id = {int(x.get("id", -1)): x for x in data if isinstance(x, dict)}
        logger.info(f"Mapped {len(by_id)} results by ID")
        
        results: List[Dict] = []
        for i, p in enumerate(posts):
            r = by_id.get(i)
            if not r:
                logger.warning(f"Missing analysis for post {i} ('{p['content'][:50]}...'), using heuristic fallback")
                results.append(_heuristic_sentiment(p["content"]))
                continue
            
            sentiment = str(r.get("sentiment", "neutral")).lower()
            if sentiment not in {"positive", "negative", "neutral"}:
                logger.warning(f"Invalid sentiment '{sentiment}' for post {i}, defaulting to neutral")
                sentiment = "neutral"
            
            confidence = float(r.get("confidence", 0.7))
            summary = str(r.get("summary", p["content"][:200]))
            
            logger.debug(f"Post {i}: sentiment={sentiment}, confidence={confidence:.2f}")
            
            results.append({
                "sentiment": sentiment,
                "confidence": round(max(0.0, min(1.0, confidence)), 2),
                "summary": summary[:300],
            })
        
        logger.info(f"Successfully analyzed {len(results)} posts via OpenAI")
        return results
        
    except Exception as e:
        logger.error(f"OpenAI analysis failed: {type(e).__name__}: {e}", exc_info=True)
        raise


def analyze_posts(posts: List[Dict]) -> List[Dict]:
    """Analyze posts for sentiment using OpenAI semantic extraction.
    
    Returns list aligned to input order with sentiment, confidence, summary.
    Falls back to heuristic analysis if OpenAI is unavailable or fails.
    """
    if not settings.openai_api_key:
        logger.warning("No OpenAI API key configured, using heuristic fallback")
        return [_heuristic_sentiment(p["content"]) for p in posts]

    try:
        # Lazy import to avoid dependency issues if not configured
        return _analyze_with_openai(posts)
    except Exception as e:
        logger.error(f"OpenAI analysis error, falling back to heuristics: {e}")
        # fallback to heuristic on any error
        return [_heuristic_sentiment(p["content"]) for p in posts]
