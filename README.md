# LinkedIn Sentiment Tracker (MVP)

Lightweight full-stack MVP that analyzes sentiment of **real LinkedIn posts** across three categories.

- **Backend:** FastAPI, SQLAlchemy, OpenAI GPT-4o-mini for semantic sentiment analysis
- **Data Source:** Apify LinkedIn Posts Search Scraper (no cookies required)
- **Frontend:** React + Vite + Tailwind CSS with category tabs
- **Architecture:** Model-Controller-Service (MCS)

## Categories

1. **AI News** - Latest AI model comparisons (ChatGPT, Claude, Perplexity, Grok, etc.)
2. **Career Advice** - Interview tips and engineering advice from specific LinkedIn influencers
3. **New Research** - ArXiv papers and algorithm breakthroughs

## Quick Start

### Prerequisites
- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **OpenAI API Key** (configured in `.env`)
- **Apify API Key** (configured in `.env`)

### 1) Backend Setup & Start

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# The .env file is already configured with your API keys
# OpenAI API Key: for sentiment analysis
# Apify API Key: for fetching real LinkedIn posts

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

**Backend will be running at:** http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### 2) Frontend Setup & Start

Open a **new terminal window** and run:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

**Frontend will be running at:** http://localhost:5173

### 3) Using the Application

1. Open http://localhost:5173 in your browser
2. **Select a category tab:** AI News, Career Advice, or New Research
3. Click **"Analyze New Posts"** to fetch and analyze posts for the selected category
4. View sentiment analysis results powered by OpenAI's GPT-4o-mini
5. Switch between categories to view different types of posts

**Note:** The first analysis may take 30-60 seconds as Apify scrapes LinkedIn in real-time.

**Category Details:**
- **AI News:** Searches for ChatGPT, Claude, Perplexity, Grok, GPT, AI models (any author)
- **Career Advice:** Searches for interview, career, engineer keywords from rajya-vardhan, sanchitnarula, tannika-majumder-424a5040, debarghyadas
- **New Research:** Searches for arxiv, research, LLM, algorithm, paper (any author)

## Data Flow
1. Select a category tab on the dashboard
2. Click "Analyze New Posts"
3. **Backend fetches up to 50 real LinkedIn posts** for the selected category using Apify's LinkedIn Posts Search Scraper
4. **Backend analyzes each post using OpenAI GPT-4o-mini** for semantic sentiment extraction
5. Results are stored in SQLite database with category tag and deduplication
6. Frontend displays filtered posts by category

## Endpoints
- GET `/health` – health check
- POST `/api/analyze?category=ai_news` – fetch and analyze posts by category
- GET `/api/posts?limit=50&category=ai_news` – fetch posts filtered by category
- GET `/api/trends` – aggregated sentiment statistics

## Project Structure
```
backend/
  app/                        # Core application
    main.py                   # FastAPI app & CORS
    config.py                 # Environment configuration
    config_models.py          # AI model settings
    controllers/
      sentiment.py            # API endpoints
    services/
      scraper.py              # Apify LinkedIn scraper
      analyzer.py             # OpenAI sentiment analysis
    models/
      schemas.py              # Pydantic response models
    database/
      connection.py           # SQLAlchemy engine
      models.py               # ORM models
  tests/                      # Unit tests
    test_data_extraction.py   # Data parsing tests
    test_scraper.py           # Apify integration tests
    test_analyzer.py          # OpenAI integration tests
  scripts/                    # Maintenance scripts
    migrate_add_role.py       # Database migrations
    cleanup_author_dicts.py   # Data cleanup
    backfill_post_metadata.py # Extract titles/URLs
  requirements.txt
  .env
  DEBUGGING.md

frontend/
  src/
    components/
      Dashboard.jsx           # Main dashboard
      SentimentChart.jsx      # Trend visualization
      PostsList.jsx           # Post display
    services/
      api.js                  # API client
    App.jsx
    main.jsx
    index.css
  package.json
  vite.config.js
```

## Configuration
Environment variables in `backend/.env` (already configured):
```
OPENAI_API_KEY=sk-proj-...  # Required for semantic sentiment analysis
APIPY_API_KEY=apify_api_...  # Required for fetching real LinkedIn posts
DATABASE_URL=sqlite:///./sentiment.db  # SQLite for local development
FRONTEND_ORIGIN=http://localhost:5173
```

Frontend can point to a custom API base by setting:
```
# in .env.local or when starting vite
VITE_API_BASE_URL=http://localhost:8000
```

## Testing

Run comprehensive tests to verify everything works:

```bash
cd backend

# Run all tests
python tests/test_data_extraction.py  # Data extraction logic
python tests/test_scraper.py          # Apify API integration
python tests/test_analyzer.py         # OpenAI API integration
```

### What the tests verify:
- ✅ Author extracted as string (not dict)
- ✅ Post titles and URLs extracted correctly
- ✅ All required fields present
- ✅ Apify API connection working
- ✅ OpenAI API connection working
- ✅ gpt-5-nano model configured correctly

See `backend/tests/README.md` for detailed test documentation.

## Database Migration

If you have an existing database, run migrations:

```bash
cd backend

# Add category column (v2.1)
python3 scripts/migrate_add_category.py

# Add role/title/url columns (v2.0)
python3 scripts/migrate_add_role.py

# Clean up old data (if upgrading from v1.0)
python3 scripts/cleanup_author_dicts.py
python3 scripts/backfill_post_metadata.py
```

See `backend/scripts/README.md` for script documentation.

## Troubleshooting

### Common Issues

**Slow first analysis:** Apify scraping takes 30-60 seconds. Check backend logs for progress.

**No posts fetched:** Verify Apify API key is correct. Falls back to mock data if API fails.

**OpenAI errors:** Falls back to heuristic sentiment analysis automatically.

**Missing dependencies:** 
```bash
cd backend
pip install -r requirements.txt
```

**CORS errors:** Backend allows `http://localhost:5173` by default.

**JSON in author field:** Run tests to verify:
```bash
python tests/test_data_extraction.py
```

**Missing columns:** Run migration:
```bash
python scripts/migrate_add_role.py
```

**Module not found errors:** Make sure you're in the backend directory and venv is activated.

See `backend/DEBUGGING.md` for detailed troubleshooting steps.

## Features
- ✅ **Three distinct categories** - AI News, Career Advice, New Research
- ✅ **Smart filtering** - Career advice filtered by specific LinkedIn influencers
- ✅ **Real LinkedIn data** via Apify (no cookies/login required)
- ✅ **AI-powered sentiment analysis** using OpenAI gpt-5-nano
- ✅ **Category-specific search queries** - tailored for each content type
- ✅ **Post titles and URLs** - clickable links to original LinkedIn posts
- ✅ **Structured author display** - name, role, and company shown separately
- ✅ **Tab-based navigation** - easy switching between categories
- ✅ **Automatic deduplication** prevents analyzing the same post twice
- ✅ **Graceful fallbacks** for both scraping and analysis
- ✅ **Clean, focused UI** for post browsing
- ✅ **Comprehensive testing** with data extraction validation
- ✅ **Fast local development** with SQLite

## Recent Updates

### v2.1 - Category-Based Dashboard (2025-10-06)

**New Features:**
- **Three content categories** with dedicated tabs:
  - AI News - Model comparisons (ChatGPT, Claude, Perplexity, Grok)
  - Career Advice - Tips from specific LinkedIn influencers
  - New Research - ArXiv papers and algorithm breakthroughs
- **Smart author filtering** for career advice category
- **Category-specific search queries** optimized for each content type
- **Simplified UI** - Removed generic insights cards, focus on posts
- **Database category field** - Posts tagged by category for filtering

**Technical Changes:**
- Added `category` column to database
- Created `migrate_add_category.py` script
- New `fetch_posts_by_category()` function in scraper
- API endpoints accept `category` parameter
- Frontend state management for active category

---

### v2.0 - Enhanced Post Display (2025-10-06)

#### Fixed JSON Display Issue
Previously, posts displayed raw JSON in the author field like:
```
{'name': 'Coding DSA', 'headline': '161 followers', ...}
```

Now properly extracts and displays:
- **Author name** (bold, prominent)
- **Role/Title** (smaller, gray)
- **Company** (smaller, lighter gray)

### New Post Display
Posts now show:
- **Title as header** (clickable link to LinkedIn)
- **Sentiment badge** (top right)
- **Author info** (smaller, bottom right)
- **Post summary** (main content area)
- **Date** (bottom left)

### Enhanced Data Extraction
- Handles author as dictionary or string
- Extracts post titles and URLs
- Validates all fields are strings (no JSON objects)
- Comprehensive logging for debugging

## Notes
- Searches for posts containing "AI", "LLM", "GPT-5", or "Claude" keywords
- Fetches up to 50 posts per analysis run using the official Apify client
- Uses **gpt-5-nano** for sentiment analysis (configurable in `app/config_models.py`)
- Apify actor runs may take 30-60 seconds to complete
- Results are cached in SQLite to avoid re-analyzing duplicate posts
