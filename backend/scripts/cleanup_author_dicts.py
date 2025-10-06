#!/usr/bin/env python3
"""
Clean up database records where author field contains JSON dict strings.
Extracts the actual name from the dict and updates the database.

Usage: python cleanup_author_dicts.py
"""

import sys
import sqlite3
import json
import re
from pathlib import Path

def parse_author_dict(author_str):
    """Extract name, company, and role from a dict string."""
    if not author_str or not author_str.startswith('{'):
        # Already clean
        return None
    
    try:
        # Try to parse as JSON
        data = json.loads(author_str.replace("'", '"'))
        name = data.get('name', 'Unknown')
        headline = data.get('headline', '')
        
        # Try to split headline into role and company
        # Common patterns: "Role at Company" or "Role | Company" or just "Company"
        role = ""
        company = headline
        
        if ' at ' in headline:
            parts = headline.split(' at ', 1)
            role = parts[0].strip()
            company = parts[1].strip()
        elif ' | ' in headline:
            parts = headline.split(' | ', 1)
            role = parts[0].strip()
            company = parts[1].strip()
        
        return {
            'name': name,
            'company': company[:255] if company else '',  # Limit to column size
            'role': role[:255] if role else ''
        }
    except Exception as e:
        print(f"  ✗ Failed to parse: {e}")
        return None


def cleanup_database():
    """Clean up author dict strings in the database."""
    db_path = Path("sentiment.db")
    
    if not db_path.exists():
        print(f"✗ Database {db_path} doesn't exist")
        return False
    
    print(f"Cleaning up database: {db_path}\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find all records with dict-like author fields
        cursor.execute("SELECT id, author, company, role FROM sentiment_posts WHERE author LIKE '{%'")
        rows = cursor.fetchall()
        
        if not rows:
            print("✓ No cleanup needed - all author fields are clean!")
            conn.close()
            return True
        
        print(f"Found {len(rows)} records with dict author fields\n")
        
        cleaned = 0
        failed = 0
        
        for row_id, author_str, existing_company, existing_role in rows:
            print(f"Record ID {row_id}:")
            print(f"  Before: {author_str[:100]}...")
            
            parsed = parse_author_dict(author_str)
            
            if parsed:
                # Update the record
                cursor.execute("""
                    UPDATE sentiment_posts 
                    SET author = ?, company = ?, role = ?
                    WHERE id = ?
                """, (parsed['name'], parsed['company'], parsed['role'], row_id))
                
                print(f"  ✓ After: {parsed['name']}")
                print(f"    Company: {parsed['company'][:60]}...")
                print(f"    Role: {parsed['role'][:60]}...")
                cleaned += 1
            else:
                print(f"  ✗ Could not parse, leaving as-is")
                failed += 1
            print()
        
        conn.commit()
        
        print("="*60)
        print(f"✓ Cleanup complete!")
        print(f"  Cleaned: {cleaned} records")
        print(f"  Failed: {failed} records")
        print("="*60)
        
        # Show sample of cleaned data
        cursor.execute("SELECT id, author, company, role FROM sentiment_posts ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        
        print("\nSample of cleaned data:")
        for row_id, author, company, role in rows:
            print(f"  ID {row_id}: {author} - {role} at {company if company else 'N/A'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("DATABASE CLEANUP: Fix Author Dict Strings")
    print("="*60)
    print()
    
    success = cleanup_database()
    
    print()
    if success:
        print("✓ Cleanup successful!")
        print("\nYou can now refresh the frontend to see clean data.")
    else:
        print("✗ Cleanup failed!")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
