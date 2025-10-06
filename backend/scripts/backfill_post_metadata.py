#!/usr/bin/env python3
"""
Backfill post_title and post_url from content field.
Extracts title/URL from content dicts and generates titles from text content.

Usage: python backfill_post_metadata.py
"""

import sys
import sqlite3
import json
import ast
from pathlib import Path

def extract_title_and_url(content_str):
    """Extract title and URL from content field."""
    if not content_str:
        return None, None
    
    # Try to parse as dict/JSON
    if content_str.strip().startswith('{'):
        try:
            # Try JSON first
            data = json.loads(content_str.replace("'", '"'))
        except:
            try:
                # Try literal eval
                data = ast.literal_eval(content_str)
            except:
                # Can't parse, generate title from text
                first_sentence = content_str.split('.')[0].strip()
                title = first_sentence[:80] + "..." if len(first_sentence) > 80 else first_sentence
                return title, None
        
        # Extract from dict structure
        if isinstance(data, dict):
            # Check for article structure
            if 'article' in data and isinstance(data['article'], dict):
                article = data['article']
                title = article.get('title', '')
                url = article.get('url', '')
                return title, url
            
            # Check for direct title/url
            title = data.get('title', '')
            url = data.get('url', '')
            
            if not title:
                # Try to extract text for title
                text = data.get('text', '') or data.get('question', '')
                if text:
                    first_sentence = text.split('.')[0].strip()
                    title = first_sentence[:80] + "..." if len(first_sentence) > 80 else first_sentence
            
            return title, url
    
    # Plain text - generate title from first sentence
    first_sentence = content_str.split('.')[0].strip()
    if len(first_sentence) > 80:
        title = first_sentence[:77] + "..."
    else:
        title = first_sentence if first_sentence else "LinkedIn Post"
    
    return title, None


def backfill_database():
    """Backfill post_title and post_url from content."""
    db_path = Path("sentiment.db")
    
    if not db_path.exists():
        print(f"✗ Database {db_path} doesn't exist")
        return False
    
    print(f"Backfilling database: {db_path}\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find all records with empty post_title
        cursor.execute("SELECT id, content, post_url FROM sentiment_posts WHERE post_title IS NULL OR post_title = ''")
        rows = cursor.fetchall()
        
        if not rows:
            print("✓ No backfill needed - all posts have titles!")
            conn.close()
            return True
        
        print(f"Found {len(rows)} posts needing titles\n")
        
        updated = 0
        failed = 0
        
        for row_id, content, existing_url in rows:
            title, url = extract_title_and_url(content)
            
            # Use existing URL if we didn't extract one
            if not url:
                url = existing_url or ""
            
            # Default title if extraction failed
            if not title:
                title = "LinkedIn Post"
            
            print(f"Record ID {row_id}:")
            print(f"  Title: {title[:80]}...")
            print(f"  URL: {url[:80] if url else 'N/A'}...")
            
            try:
                cursor.execute("""
                    UPDATE sentiment_posts 
                    SET post_title = ?, post_url = ?
                    WHERE id = ?
                """, (title, url, row_id))
                updated += 1
                print(f"  ✓ Updated")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                failed += 1
            
            print()
        
        conn.commit()
        
        print("="*60)
        print(f"✓ Backfill complete!")
        print(f"  Updated: {updated} records")
        print(f"  Failed: {failed} records")
        print("="*60)
        
        # Show sample of updated data
        cursor.execute("SELECT id, post_title, post_url FROM sentiment_posts WHERE post_title IS NOT NULL ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        
        print("\nSample of updated posts:")
        for row_id, title, url in rows:
            url_display = url[:50] + "..." if url and len(url) > 50 else (url or "No URL")
            print(f"  ID {row_id}: {title[:60]}...")
            print(f"           {url_display}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Backfill failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("DATABASE BACKFILL: Post Titles and URLs")
    print("="*60)
    print()
    
    success = backfill_database()
    
    print()
    if success:
        print("✓ Backfill successful!")
        print("\nRestart the backend and refresh the frontend to see titles with links.")
    else:
        print("✗ Backfill failed!")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
