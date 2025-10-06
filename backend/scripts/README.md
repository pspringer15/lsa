# Database Maintenance Scripts

Utility scripts for database migrations and data cleanup.

## Scripts

### migrate_add_role.py
Adds new columns to the database schema.

**Purpose:** Add `role`, `post_title`, and `post_url` columns to existing databases.

**When to use:**
- After pulling latest code changes
- When upgrading from v1.0 to v2.0
- When columns are missing

**Usage:**
```bash
cd backend
python scripts/migrate_add_role.py
```

**What it does:**
1. Checks if database exists
2. Checks which columns are missing
3. Adds missing columns
4. Shows updated table structure

**Safe to run multiple times** - skips existing columns.

---

### cleanup_author_dicts.py
Fixes author fields that contain JSON dictionaries.

**Purpose:** Extract clean author names from dict strings like:
```
{'name': 'John Doe', 'headline': 'Engineer at Company', ...}
```

**When to use:**
- After importing data from old format
- If you see JSON in author fields
- One-time cleanup after v2.0 upgrade

**Usage:**
```bash
cd backend
python scripts/cleanup_author_dicts.py
```

**What it does:**
1. Finds records with dict-like author fields
2. Parses JSON/dict strings
3. Extracts name, company, role
4. Updates database records
5. Shows before/after samples

**Safe to run multiple times** - only processes dict fields.

---

### backfill_post_metadata.py
Extracts titles and URLs from content field.

**Purpose:** Populate empty `post_title` and `post_url` fields from content.

**When to use:**
- After running migrate_add_role.py
- If posts show "LinkedIn Post" without titles
- One-time cleanup after v2.0 upgrade

**Usage:**
```bash
cd backend
python scripts/backfill_post_metadata.py
```

**What it does:**
1. Finds posts with empty post_title
2. Extracts title/URL from content field
3. Handles nested structures (articles, polls, etc.)
4. Generates titles from first sentence if needed
5. Updates database records

**Safe to run multiple times** - only processes empty fields.

---

## Recommended Order

For a fresh v2.0 upgrade:

```bash
cd backend

# 1. Add new columns
python scripts/migrate_add_role.py

# 2. Clean up author dicts
python scripts/cleanup_author_dicts.py

# 3. Extract titles and URLs
python scripts/backfill_post_metadata.py

# 4. Restart backend
uvicorn app.main:app --reload --port 8000
```

## Verification

After running scripts, verify:

```bash
# Check database structure
sqlite3 sentiment.db ".schema sentiment_posts"

# Check sample data
sqlite3 sentiment.db "SELECT id, author, post_title, post_url FROM sentiment_posts LIMIT 5"
```

## Backup Recommendation

Before running scripts on production data:

```bash
# Backup database
cp sentiment.db sentiment.db.backup

# Run scripts
python scripts/migrate_add_role.py
# etc...

# Restore if needed
cp sentiment.db.backup sentiment.db
```

## Troubleshooting

**Script fails with "Database doesn't exist":**
- Run the application first to create the database
- Or create an empty database with proper schema

**"Module not found" errors:**
- Make sure you're in the backend directory
- Run from backend/, not from scripts/

**No records updated:**
- Check if records actually need updating
- Scripts are idempotent and skip clean records

## Notes

- All scripts use SQLite directly (not SQLAlchemy)
- Scripts are designed to be idempotent
- Detailed logging shows what's happening
- Safe to run in any order (though recommended order is best)
