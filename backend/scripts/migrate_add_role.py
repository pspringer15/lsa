#!/usr/bin/env python3
"""
Database migration script to add new columns to sentiment_posts table.
Run this once to update existing databases.

Usage: python migrate_add_role.py
"""

import sys
import sqlite3
from pathlib import Path

def migrate_sqlite():
    """Add role, post_title, and post_url columns to SQLite database."""
    db_path = Path("sentiment.db")
    
    if not db_path.exists():
        print(f"✓ Database {db_path} doesn't exist yet - no migration needed")
        print("  All columns will be created automatically on first run")
        return True
    
    print(f"Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(sentiment_posts)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Columns to add
        new_columns = {
            'role': 'VARCHAR(255)',
            'post_title': 'VARCHAR(500)',
            'post_url': 'VARCHAR(1000)'
        }
        
        added_columns = []
        for col_name, col_type in new_columns.items():
            if col_name not in existing_columns:
                print(f"Adding '{col_name}' column...")
                cursor.execute(f"ALTER TABLE sentiment_posts ADD COLUMN {col_name} {col_type}")
                added_columns.append(col_name)
            else:
                print(f"✓ Column '{col_name}' already exists")
        
        if added_columns:
            conn.commit()
            print(f"\n✓ Migration successful!")
            print(f"  Added columns: {', '.join(added_columns)}")
        else:
            print(f"\n✓ No migration needed - all columns already exist")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(sentiment_posts)")
        columns = cursor.fetchall()
        print("\nCurrent table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("DATABASE MIGRATION: Add new columns")
    print("="*60)
    print()
    
    success = migrate_sqlite()
    
    print()
    print("="*60)
    if success:
        print("✓ Migration completed successfully!")
        print("\nYou can now restart the backend server.")
    else:
        print("✗ Migration failed!")
        print("\nPlease check the error messages above.")
    print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
