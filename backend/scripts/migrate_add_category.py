"""
Add category column to sentiment_posts table
"""
import sqlite3
import os

DB_PATH = "sentiment.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} doesn't exist yet. Skipping migration.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if category column exists
    cursor.execute("PRAGMA table_info(sentiment_posts)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "category" in columns:
        print("✅ Column 'category' already exists. Skipping.")
    else:
        print("Adding 'category' column...")
        cursor.execute("ALTER TABLE sentiment_posts ADD COLUMN category VARCHAR(50)")
        conn.commit()
        print("✅ Added 'category' column")
    
    # Show updated schema
    cursor.execute("PRAGMA table_info(sentiment_posts)")
    print("\nUpdated table structure:")
    for row in cursor.fetchall():
        print(f"  {row[1]}: {row[2]}")
    
    conn.close()
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate()
