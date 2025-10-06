#!/usr/bin/env python3
"""
Unit tests for the LinkedIn scraper service.
Run with: python test_scraper.py
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add app to path
sys.path.insert(0, '.')

from app.services.scraper import fetch_linkedin_posts, _generate_mock_posts_fallback
from app.config import settings


def test_apify_connection():
    """Test Apify API connection."""
    print("\n" + "="*80)
    print("TEST 1: Apify API Connection")
    print("="*80)
    
    if not settings.apify_api_key:
        print("✗ FAIL: No Apify API key configured")
        return False
    
    print(f"✓ API Key configured: {settings.apify_api_key[:20]}...")
    
    try:
        from apify_client import ApifyClient
        client = ApifyClient(settings.apify_api_key)
        
        print("✓ ApifyClient initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {type(e).__name__}: {e}")
        return False


def test_fetch_linkedin_posts():
    """Test fetching real LinkedIn posts."""
    print("\n" + "="*80)
    print("TEST 2: Fetch LinkedIn Posts")
    print("="*80)
    
    print("\nFetching posts (this may take 30-60 seconds)...")
    
    try:
        posts = fetch_linkedin_posts(search_queries=["AI"], max_posts=5)
        
        print(f"\n✓ Fetched {len(posts)} posts")
        
        for i, post in enumerate(posts[:3]):  # Show first 3
            print(f"\n  Post {i+1}:")
            print(f"    Title: {post.get('post_title', 'N/A')}")
            print(f"    URL: {post.get('post_url', 'N/A')}")
            print(f"    Author: {post.get('author', 'N/A')}")
            print(f"    Company: {post.get('company', 'N/A')}")
            print(f"    Role: {post.get('role', 'N/A')}")
            print(f"    Content: {post.get('content', '')[:100]}...")
            print(f"    Date: {post.get('post_date')}")
            
            # Verify no dict in author field
            author = post.get('author', '')
            if isinstance(author, dict) or (isinstance(author, str) and author.startswith('{')):
                print(f"    ✗ ERROR: Author is a dict/JSON: {author}")
                return False
        
        # Validate structure
        if posts:
            required_keys = ['author', 'company', 'role', 'post_title', 'post_url', 'content', 'post_date']
            first_post = posts[0]
            missing_keys = [k for k in required_keys if k not in first_post]
            
            if missing_keys:
                print(f"\n⚠️  Warning: Missing keys in post: {missing_keys}")
            else:
                print(f"\n✓ All required keys present")
            
            # Verify all string fields are actually strings
            for key in ['author', 'company', 'role', 'post_title', 'post_url', 'content']:
                value = first_post.get(key)
                if value and not isinstance(value, str):
                    print(f"\n✗ ERROR: {key} is not a string: {type(value)}")
                    return False
            
            print(f"✓ All fields are correct types")
        
        return len(posts) > 0
        
    except Exception as e:
        print(f"\n✗ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_fallback():
    """Test the mock data fallback."""
    print("\n" + "="*80)
    print("TEST 3: Mock Data Fallback")
    print("="*80)
    
    try:
        posts = _generate_mock_posts_fallback(5)
        
        print(f"\n✓ Generated {len(posts)} mock posts")
        
        for i, post in enumerate(posts[:2]):
            print(f"\n  Post {i+1}:")
            print(f"    Author: {post.get('author')}")
            print(f"    Content: {post.get('content')[:60]}...")
        
        return len(posts) > 0
        
    except Exception as e:
        print(f"\n✗ FAIL: {type(e).__name__}: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("LINKEDIN SCRAPER UNIT TESTS")
    print("="*80)
    
    results = []
    
    # Test 1: Apify connection
    apify_works = test_apify_connection()
    results.append(("Apify Connection", apify_works))
    
    # Test 2: Fetch posts (only if Apify works)
    if apify_works:
        fetch_works = test_fetch_linkedin_posts()
        results.append(("Fetch LinkedIn Posts", fetch_works))
    else:
        print("\n⚠️  Skipping fetch test due to Apify connection failure")
    
    # Test 3: Mock fallback (always run)
    mock_works = test_mock_fallback()
    results.append(("Mock Fallback", mock_works))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    return all(passed for _, passed in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
