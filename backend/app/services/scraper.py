from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from apify_client import ApifyClient
from app.config import settings

logger = logging.getLogger(__name__)


def _parse_linkedin_date(date_str: str) -> datetime:
    """Parse LinkedIn date strings like '2d', '1w', '3mo' into datetime objects."""
    if not date_str:
        return datetime.utcnow()
    
    # Handle dict or non-string inputs
    if not isinstance(date_str, str):
        return datetime.utcnow()
    
    date_str = date_str.strip().lower()
    now = datetime.utcnow()
    
    try:
        # Handle relative dates: "2d", "1w", "3mo", "1y"
        if date_str.endswith('d'):
            days = int(date_str[:-1])
            return now - timedelta(days=days)
        elif date_str.endswith('w'):
            weeks = int(date_str[:-1])
            return now - timedelta(weeks=weeks)
        elif date_str.endswith('mo'):
            months = int(date_str[:-2])
            return now - timedelta(days=months * 30)
        elif date_str.endswith('y'):
            years = int(date_str[:-1])
            return now - timedelta(days=years * 365)
        elif date_str.endswith('h'):
            hours = int(date_str[:-1])
            return now - timedelta(hours=hours)
        elif date_str.endswith('m'):
            minutes = int(date_str[:-1])
            return now - timedelta(minutes=minutes)
        else:
            # Try parsing as ISO date
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        logger.warning(f"Could not parse date: {date_str}, using current time")
        return now


def fetch_linkedin_posts(search_queries: List[str] = None, max_posts: int = 50) -> List[Dict]:
    """Fetch real LinkedIn posts using Apify LinkedIn Posts Search Scraper API.
    
    Args:
        search_queries: List of search terms (default: ["AI", "LLM", "GPT-5", "Claude"])
        max_posts: Maximum number of posts to fetch (default: 50)
    
    Returns:
        List of normalized post dictionaries
    """
    if not settings.apify_api_key:
        logger.warning("No Apify API key configured, falling back to mock data")
        return _generate_mock_posts_fallback()
    
    if search_queries is None:
        search_queries = ["AI", "LLM", "GPT-5", "Claude"]
    
    try:
        # Initialize the ApifyClient
        client = ApifyClient(settings.apify_api_key)
        
        # Prepare input for the Actor
        run_input = {
            "search_keyword": " ".join(search_queries),  # Combine queries
            "sort_by": "date_posted",  # Get recent posts
            "page_number": 1,  # First page
        }
        
        # Run the Actor and wait for it to finish
        logger.info(f"Starting Apify actor for queries: {search_queries}")
        run = client.actor("apimaestro/linkedin-posts-search-scraper-no-cookies").call(run_input=run_input)
        
        # Fetch results from the dataset
        items = client.dataset(run["defaultDatasetId"]).list_items().items
        logger.info(f"Fetched {len(items)} posts from Apify")
        
        # Normalize the posts
        normalized_posts = []
        for post in items[:max_posts]:
            logger.debug(f"Processing post: {list(post.keys())[:10]}")
            
            # Extract relevant fields from Apify response
            # Handle content which might be a string or dict
            content_raw = post.get("postContent") or post.get("content") or post.get("text") or ""
            
            # Initialize title and URL from content if it's structured
            extracted_title = ""
            extracted_url = ""
            
            # If content is a dict, try to extract text AND metadata from it
            if isinstance(content_raw, dict):
                # Check for article structure
                if 'article' in content_raw and isinstance(content_raw['article'], dict):
                    article = content_raw['article']
                    extracted_title = article.get('title', '')
                    extracted_url = article.get('url', '')
                    content = article.get('text', '') or str(content_raw)
                else:
                    # Extract title/url if present
                    extracted_title = content_raw.get('title', '')
                    extracted_url = content_raw.get('url', '')
                    # Try to get text content
                    content = content_raw.get("text", "") or content_raw.get("content", "") or content_raw.get("question", "") or str(content_raw)
            else:
                content = str(content_raw) if content_raw else ""
            
            # Extract author information - handle dict or string
            author_raw = post.get("authorName") or post.get("author") or post.get("name") or {}
            if isinstance(author_raw, dict):
                # Author is a dict like {'name': 'Coding DSA', 'headline': '...', ...}
                author = author_raw.get("name", "") or author_raw.get("authorName", "") or "Unknown"
                company = author_raw.get("headline", "") or ""
                role = author_raw.get("headline", "") or ""
            else:
                author = str(author_raw) if author_raw else "Unknown"
                company = post.get("authorCompany") or post.get("company") or ""
                role = post.get("authorTitle") or post.get("authorRole") or post.get("headline") or ""
            
            # Extract post metadata - prioritize extracted from content dict
            post_title = extracted_title or post.get("postTitle") or post.get("title") or ""
            post_url = extracted_url or post.get("postUrl") or post.get("post_url") or post.get("url") or post.get("link") or ""
            
            # Generate title from content if not provided
            if not post_title and content:
                # Use first sentence or first 80 chars as title
                first_sentence = content.split('.')[0].strip()
                if len(first_sentence) > 80:
                    post_title = first_sentence[:77] + "..."
                else:
                    post_title = first_sentence
            
            post_date_str = post.get("postedDate") or post.get("date") or post.get("publishedAt") or post.get("posted_at") or ""
            
            # Ensure we have valid string content
            if not content or not isinstance(content, str) or len(content.strip()) < 10:
                logger.debug(f"Skipping post with invalid content")
                continue  # Skip empty or very short posts
            
            # Final validation - ensure no dicts made it through
            author = str(author).strip() if author else "Unknown"
            if author.startswith('{'):
                logger.warning(f"Detected dict in author field, extracting manually")
                # Emergency fallback - extract from string representation
                try:
                    import ast
                    author_dict = ast.literal_eval(author)
                    author = author_dict.get('name', 'Unknown')
                except:
                    author = "Unknown"
            
            normalized_posts.append({
                "author": author,
                "company": str(company).strip() if company else "",
                "role": str(role).strip() if role else "",
                "post_title": str(post_title).strip() if post_title else "",
                "post_url": str(post_url).strip() if post_url else "",
                "content": content.strip(),
                "post_date": _parse_linkedin_date(post_date_str) if post_date_str else datetime.utcnow(),
            })
            
            logger.debug(f"Normalized post: author={author}, title={post_title[:50] if post_title else 'N/A'}")
        
        if not normalized_posts:
            logger.warning("No valid posts found in Apify response, using fallback")
            return _generate_mock_posts_fallback()
        
        logger.info(f"Successfully normalized {len(normalized_posts)} posts")
        return normalized_posts
        
    except Exception as e:
        logger.error(f"Error fetching LinkedIn posts from Apify: {e}", exc_info=True)
        return _generate_mock_posts_fallback()


def _generate_mock_posts_fallback(n: int = 12) -> List[Dict]:
    """Fallback mock data generator when Apify API is unavailable."""
    logger.info("Using mock data fallback")
    
    mock_posts = [
        {
            "author": "Sarah Chen",
            "company": "TechCorp",
            "role": "VP of Customer Success",
            "post_title": "GPT-5 Transforms Our Customer Service",
            "post_url": "https://www.linkedin.com/posts/example1",
            "content": "Just implemented GPT-5 in our customer service workflow. Response time down 70%, customer satisfaction up 45%! The reasoning capabilities are game-changing. #AI #CustomerSuccess",
            "date": "2025-01-28",
        },
        {
            "author": "Michael Rodriguez",
            "company": "StartupXYZ",
            "role": "Senior Software Engineer",
            "post_title": "Claude 3.7 Sonnet for Code Reviews",
            "post_url": "https://www.linkedin.com/posts/example2",
            "content": "Anthropic's Claude 3.7 Sonnet is now our go-to for code reviews. Caught 3 critical bugs our senior devs missed. The future of development is here! #CodingAI #Claude",
            "date": "2025-01-27",
        },
        {
            "author": "Lisa Park",
            "company": "FinanceHub",
            "role": "Chief Risk Officer",
            "post_title": "AI in Finance: Proceed with Caution",
            "post_url": "https://www.linkedin.com/posts/example3",
            "content": "Warning: Our tests show GPT-5's financial analysis still hallucinates 15% of the time. Great tool, but human oversight remains critical. #AIEthics #FinTech",
            "date": "2025-01-26",
        },
    ]
    
    # Normalize structure
    normalized = []
    for p in mock_posts[:n]:
        dt = datetime.fromisoformat(str(p["date"]))
        normalized.append({
            "author": p.get("author"),
            "company": p.get("company"),
            "role": p.get("role", ""),
            "post_title": p.get("post_title", ""),
            "post_url": p.get("post_url", ""),
            "content": p["content"],
            "post_date": dt,
        })
    return normalized


def fetch_posts_by_category(category: str, max_posts: int = 50) -> List[Dict]:
    """Fetch LinkedIn posts by category with specific search queries and author filters.
    
    Categories:
    - ai_news: Latest AI model comparisons and news
    - career_advice: Job/career advice from specific LinkedIn profiles
    - new_research: ArXiv papers and research breakthroughs
    
    Args:
        category: One of 'ai_news', 'career_advice', 'new_research'
        max_posts: Maximum posts to fetch (default: 50)
    
    Returns:
        List of normalized post dictionaries with category field
    """
    # Define search queries and author filters per category
    category_config = {
        "ai_news": {
            "queries": ["ChatGPT", "Claude", "Perplexity", "Grok", "GPT", "AI models"],
            "author_filters": []  # Any author
        },
        "career_advice": {
            "queries": ["Rajya Vardhan", "Sanchit Narula", "Tannika Majumder", "Debarghya Das"],
            "author_filters": []  # Search by author names directly
        },
        "new_research": {
            "queries": ["arxiv", "research", "LLM", "algorithm", "paper"],
            "author_filters": []  # Any author
        }
    }
    
    if category not in category_config:
        logger.warning(f"Unknown category: {category}, defaulting to ai_news")
        category = "ai_news"
    
    config = category_config[category]
    posts = fetch_linkedin_posts(search_queries=config["queries"], max_posts=max_posts)
    
    # Filter by author if specified
    if config["author_filters"]:
        filtered_posts = []
        for post in posts:
            post_url = post.get("post_url", "")
            # Check if any of the target profiles are in the post URL
            if any(profile in post_url.lower() for profile in config["author_filters"]):
                filtered_posts.append(post)
        posts = filtered_posts
        logger.info(f"Filtered to {len(posts)} posts from target authors")
    
    # Add category to each post
    for post in posts:
        post["category"] = category
    
    return posts


# Maintain backward compatibility
def generate_mock_posts(n: int = 12) -> List[Dict]:
    """Main entry point - fetches real LinkedIn posts or falls back to mock data."""
    return fetch_linkedin_posts(search_queries=["AI", "LLM", "GPT-5", "Claude"], max_posts=50)
