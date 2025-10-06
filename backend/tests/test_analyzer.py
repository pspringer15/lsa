#!/usr/bin/env python3
"""
Unit tests for the sentiment analyzer service.
Run with: python test_analyzer.py
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add app to path
sys.path.insert(0, '.')

from app.services.analyzer import analyze_posts, _analyze_with_openai, _heuristic_sentiment
from app.config import settings

def test_heuristic_sentiment():
    """Test the heuristic fallback analyzer."""
    print("\n" + "="*80)
    print("TEST 1: Heuristic Sentiment Analysis")
    print("="*80)
    
    test_cases = [
        {
            "content": "GPT-5 is amazing! Productivity gains are incredible. Game-changing technology!",
            "expected": "positive"
        },
        {
            "content": "Warning: AI hallucinates frequently. Major regression in accuracy. Serious issues.",
            "expected": "negative"
        },
        {
            "content": "The model was released yesterday. It has new features.",
            "expected": "neutral"
        }
    ]
    
    for i, test in enumerate(test_cases):
        result = _heuristic_sentiment(test["content"])
        print(f"\nTest {i+1}:")
        print(f"  Content: {test['content'][:60]}...")
        print(f"  Expected: {test['expected']}")
        print(f"  Got: {result['sentiment']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  ✓ PASS" if result['sentiment'] == test['expected'] else f"  ✗ FAIL")


def test_openai_api_connection():
    """Test OpenAI API connection and authentication."""
    print("\n" + "="*80)
    print("TEST 2: OpenAI API Connection")
    print("="*80)
    
    if not settings.openai_api_key:
        print("✗ FAIL: No OpenAI API key configured")
        return False
    
    print(f"✓ API Key configured: {settings.openai_api_key[:20]}...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Test with a simple completion
        print("\nTesting simple API call...")
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test successful' in JSON format"}],
            response_format={"type": "json_object"},
            max_tokens=50
        )
        
        print(f"✓ API call successful")
        print(f"  Model: {resp.model}")
        print(f"  Usage: {resp.usage}")
        print(f"  Response: {resp.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {type(e).__name__}: {e}")
        return False


def test_openai_sentiment_analysis():
    """Test OpenAI sentiment analysis with sample posts."""
    print("\n" + "="*80)
    print("TEST 3: OpenAI Sentiment Analysis")
    print("="*80)
    
    test_posts = [
        {
            "content": "Just implemented GPT-5 in our customer service workflow. Response time down 70%, customer satisfaction up 45%! The reasoning capabilities are game-changing.",
            "author": "Test User 1",
            "company": "TestCorp",
            "post_date": datetime.utcnow()
        },
        {
            "content": "Warning: Our tests show GPT-5's financial analysis still hallucinates 15% of the time. Great tool, but human oversight remains critical.",
            "author": "Test User 2",
            "company": "FinanceTest",
            "post_date": datetime.utcnow()
        },
        {
            "content": "Claude 4 was released today. It includes new features for code generation and analysis.",
            "author": "Test User 3",
            "company": "TechTest",
            "post_date": datetime.utcnow()
        }
    ]
    
    print(f"\nAnalyzing {len(test_posts)} test posts...")
    
    try:
        results = _analyze_with_openai(test_posts)
        
        print(f"\n✓ Analysis completed successfully")
        print(f"  Analyzed {len(results)} posts")
        
        for i, (post, result) in enumerate(zip(test_posts, results)):
            print(f"\n  Post {i+1}:")
            print(f"    Content: {post['content'][:60]}...")
            print(f"    Sentiment: {result['sentiment']}")
            print(f"    Confidence: {result['confidence']}")
            print(f"    Summary: {result['summary'][:80]}...")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_analyze_posts():
    """Test the full analyze_posts function with fallback logic."""
    print("\n" + "="*80)
    print("TEST 4: Full analyze_posts() Function")
    print("="*80)
    
    test_posts = [
        {
            "content": "AI is transforming healthcare with amazing results!",
            "author": "Dr. Smith",
            "company": "HealthAI",
            "post_date": datetime.utcnow()
        },
        {
            "content": "Concerns about AI bias in hiring algorithms continue to grow.",
            "author": "Jane Doe",
            "company": "HRTech",
            "post_date": datetime.utcnow()
        }
    ]
    
    print(f"\nAnalyzing {len(test_posts)} posts with full function...")
    
    try:
        results = analyze_posts(test_posts)
        
        print(f"\n✓ Analysis completed")
        print(f"  Results: {len(results)} posts")
        
        for i, result in enumerate(results):
            print(f"\n  Post {i+1}:")
            print(f"    Sentiment: {result['sentiment']}")
            print(f"    Confidence: {result['confidence']}")
            print(f"    Summary: {result['summary'][:60]}...")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SENTIMENT ANALYZER UNIT TESTS")
    print("="*80)
    
    results = []
    
    # Test 1: Heuristic sentiment
    test_heuristic_sentiment()
    
    # Test 2: OpenAI API connection
    api_works = test_openai_api_connection()
    results.append(("OpenAI API Connection", api_works))
    
    if api_works:
        # Test 3: OpenAI sentiment analysis
        openai_works = test_openai_sentiment_analysis()
        results.append(("OpenAI Sentiment Analysis", openai_works))
        
        # Test 4: Full function
        full_works = test_full_analyze_posts()
        results.append(("Full analyze_posts()", full_works))
    else:
        print("\n⚠️  Skipping OpenAI tests due to API connection failure")
    
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
