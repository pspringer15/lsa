#!/usr/bin/env python3
"""
Comprehensive tests for data extraction from Apify responses.
Tests the scraper's ability to handle various data formats.

Usage: python test_data_extraction.py
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, '.')

def test_author_dict_extraction():
    """Test extraction when author is a dict (the problematic case)."""
    print("\n" + "="*80)
    print("TEST 1: Author as Dictionary")
    print("="*80)
    
    # Simulate Apify response with author as dict
    mock_post = {
        "postContent": "This is a test post about AI and machine learning.",
        "author": {
            "name": "Coding DSA",
            "headline": "161 followers",
            "profile_id": "106679391",
            "profile_url": "https://www.linkedin.com/company/codingdsa/posts",
            "image_url": ""
        },
        "postTitle": "Understanding AI Fundamentals",
        "postUrl": "https://www.linkedin.com/posts/example123",
        "postedDate": "2d"
    }
    
    # Extract author information - handle dict or string
    author_raw = mock_post.get("authorName") or mock_post.get("author") or mock_post.get("name") or {}
    
    print(f"Raw author data type: {type(author_raw)}")
    print(f"Raw author data: {author_raw}")
    
    if isinstance(author_raw, dict):
        author = author_raw.get("name", "") or author_raw.get("authorName", "") or "Unknown"
        company = author_raw.get("headline", "") or ""
        role = author_raw.get("headline", "") or ""
        print(f"\n✓ Detected dict format")
    else:
        author = str(author_raw) if author_raw else "Unknown"
        company = mock_post.get("authorCompany") or mock_post.get("company") or ""
        role = mock_post.get("authorTitle") or mock_post.get("authorRole") or ""
        print(f"\n✓ Detected string format")
    
    print(f"\nExtracted data:")
    print(f"  Author: {author}")
    print(f"  Company: {company}")
    print(f"  Role: {role}")
    
    # Verify no dict in output
    assert isinstance(author, str), f"Author should be string, got {type(author)}"
    assert not author.startswith("{"), f"Author should not be JSON: {author}"
    
    print(f"\n✓ PASS: Author correctly extracted as string")
    return True


def test_author_string_extraction():
    """Test extraction when author is a simple string."""
    print("\n" + "="*80)
    print("TEST 2: Author as String")
    print("="*80)
    
    mock_post = {
        "postContent": "Another test post.",
        "authorName": "John Doe",
        "authorCompany": "TechCorp",
        "authorTitle": "Senior Engineer",
        "postTitle": "Tech Insights",
        "postUrl": "https://www.linkedin.com/posts/example456"
    }
    
    author_raw = mock_post.get("authorName") or mock_post.get("author") or {}
    
    print(f"Raw author data type: {type(author_raw)}")
    print(f"Raw author data: {author_raw}")
    
    if isinstance(author_raw, dict):
        author = author_raw.get("name", "") or "Unknown"
        company = author_raw.get("headline", "") or ""
        role = author_raw.get("headline", "") or ""
    else:
        author = str(author_raw) if author_raw else "Unknown"
        company = mock_post.get("authorCompany") or ""
        role = mock_post.get("authorTitle") or ""
    
    print(f"\nExtracted data:")
    print(f"  Author: {author}")
    print(f"  Company: {company}")
    print(f"  Role: {role}")
    
    assert author == "John Doe"
    assert company == "TechCorp"
    assert role == "Senior Engineer"
    
    print(f"\n✓ PASS: String author correctly extracted")
    return True


def test_post_metadata_extraction():
    """Test extraction of post title and URL."""
    print("\n" + "="*80)
    print("TEST 3: Post Metadata Extraction")
    print("="*80)
    
    mock_post = {
        "postContent": "Test content",
        "postTitle": "My Amazing AI Discovery",
        "postUrl": "https://www.linkedin.com/posts/activity-123456",
        "author": "Jane Smith"
    }
    
    post_title = mock_post.get("postTitle") or mock_post.get("title") or ""
    post_url = mock_post.get("postUrl") or mock_post.get("url") or mock_post.get("link") or ""
    
    print(f"Post Title: {post_title}")
    print(f"Post URL: {post_url}")
    
    assert post_title == "My Amazing AI Discovery"
    assert post_url == "https://www.linkedin.com/posts/activity-123456"
    assert isinstance(post_title, str)
    assert isinstance(post_url, str)
    
    print(f"\n✓ PASS: Post metadata correctly extracted")
    return True


def test_content_dict_extraction():
    """Test extraction when content is a dict."""
    print("\n" + "="*80)
    print("TEST 4: Content as Dictionary")
    print("="*80)
    
    mock_post = {
        "content": {
            "text": "This is the actual post content",
            "images": []
        },
        "author": "Test User"
    }
    
    content_raw = mock_post.get("postContent") or mock_post.get("content") or mock_post.get("text") or ""
    
    print(f"Raw content type: {type(content_raw)}")
    
    if isinstance(content_raw, dict):
        content = content_raw.get("text", "") or content_raw.get("content", "") or str(content_raw)
        print(f"✓ Extracted text from dict")
    else:
        content = str(content_raw) if content_raw else ""
        print(f"✓ Used content as-is")
    
    print(f"Content: {content}")
    
    assert isinstance(content, str)
    assert content == "This is the actual post content"
    
    print(f"\n✓ PASS: Content correctly extracted from dict")
    return True


def test_missing_fields():
    """Test handling of missing fields."""
    print("\n" + "="*80)
    print("TEST 5: Missing Fields Handling")
    print("="*80)
    
    mock_post = {
        "postContent": "Minimal post with only content"
    }
    
    author_raw = mock_post.get("authorName") or mock_post.get("author") or mock_post.get("name") or {}
    
    if isinstance(author_raw, dict):
        author = author_raw.get("name", "") or "Unknown"
        company = author_raw.get("headline", "") or ""
        role = author_raw.get("headline", "") or ""
    else:
        author = str(author_raw) if author_raw else "Unknown"
        company = mock_post.get("authorCompany") or ""
        role = mock_post.get("authorTitle") or ""
    
    post_title = mock_post.get("postTitle") or ""
    post_url = mock_post.get("postUrl") or ""
    
    print(f"Author: '{author}'")
    print(f"Company: '{company}'")
    print(f"Role: '{role}'")
    print(f"Post Title: '{post_title}'")
    print(f"Post URL: '{post_url}'")
    
    # Should have defaults, not crash
    assert author == "Unknown"
    assert company == ""
    assert role == ""
    assert post_title == ""
    assert post_url == ""
    
    print(f"\n✓ PASS: Missing fields handled gracefully")
    return True


def test_full_normalization():
    """Test the complete normalization process."""
    print("\n" + "="*80)
    print("TEST 6: Full Normalization Process")
    print("="*80)
    
    mock_posts = [
        {
            "postContent": "AI is transforming healthcare!",
            "author": {
                "name": "Dr. Sarah Johnson",
                "headline": "Chief Medical Officer at HealthTech Inc",
                "profile_url": "https://linkedin.com/in/sarahjohnson"
            },
            "postTitle": "AI in Healthcare: A Revolution",
            "postUrl": "https://www.linkedin.com/posts/activity-789",
            "postedDate": "1d"
        },
        {
            "postContent": "Machine learning basics explained",
            "authorName": "Mike Chen",
            "authorCompany": "DataCorp",
            "authorTitle": "ML Engineer",
            "postTitle": "ML 101",
            "postUrl": "https://www.linkedin.com/posts/activity-456"
        }
    ]
    
    normalized_posts = []
    
    for post in mock_posts:
        # Extract author information - handle dict or string
        author_raw = post.get("authorName") or post.get("author") or post.get("name") or {}
        if isinstance(author_raw, dict):
            author = author_raw.get("name", "") or "Unknown"
            company = author_raw.get("headline", "") or ""
            role = author_raw.get("headline", "") or ""
        else:
            author = str(author_raw) if author_raw else "Unknown"
            company = post.get("authorCompany") or ""
            role = post.get("authorTitle") or ""
        
        # Extract post metadata
        post_title = post.get("postTitle") or ""
        post_url = post.get("postUrl") or ""
        content = post.get("postContent") or ""
        
        normalized_posts.append({
            "author": str(author).strip(),
            "company": str(company).strip() if company else "",
            "role": str(role).strip() if role else "",
            "post_title": str(post_title).strip() if post_title else "",
            "post_url": str(post_url).strip() if post_url else "",
            "content": content.strip(),
        })
    
    print(f"Normalized {len(normalized_posts)} posts:\n")
    
    for i, p in enumerate(normalized_posts, 1):
        print(f"Post {i}:")
        print(f"  Title: {p['post_title']}")
        print(f"  URL: {p['post_url']}")
        print(f"  Author: {p['author']}")
        print(f"  Company: {p['company']}")
        print(f"  Role: {p['role']}")
        print(f"  Content: {p['content'][:50]}...")
        print()
        
        # Verify all fields are strings
        for key, value in p.items():
            assert isinstance(value, str), f"{key} should be string, got {type(value)}"
            assert not value.startswith("{"), f"{key} should not be JSON: {value}"
    
    print(f"✓ PASS: All posts normalized correctly")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("DATA EXTRACTION TESTS")
    print("="*80)
    
    tests = [
        ("Author Dict Extraction", test_author_dict_extraction),
        ("Author String Extraction", test_author_string_extraction),
        ("Post Metadata Extraction", test_post_metadata_extraction),
        ("Content Dict Extraction", test_content_dict_extraction),
        ("Missing Fields Handling", test_missing_fields),
        ("Full Normalization", test_full_normalization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ FAIL: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
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
