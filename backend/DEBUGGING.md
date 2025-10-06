# Debugging Guide for LinkedIn Sentiment Analysis

## Quick Diagnostics

### 1. Run Unit Tests

Test the analyzer service:
```bash
cd backend
python test_analyzer.py
```

Test the scraper service:
```bash
python test_scraper.py
```

### 2. Check Logs

The application now has comprehensive DEBUG-level logging. When you run the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

You'll see detailed logs for:
- **Scraper**: Apify API calls, post fetching, data normalization
- **Analyzer**: OpenAI API calls, prompt/response details, parsing steps

### 3. Common Issues & Solutions

#### Issue: "OpenAI analysis failed"

**Check the logs for:**
```
ERROR:app.services.analyzer:OpenAI analysis failed: <error type>
```

**Common causes:**

1. **Invalid model name** (e.g., "gpt-5-nano" doesn't exist)
   - ✅ Fixed: Now using `gpt-4o-mini`
   - Check line 109 in `analyzer.py`

2. **JSON parsing error**
   - Look for: `JSON parsing failed: <details>`
   - The response format might not match expectations
   - Check the "Full OpenAI response" debug log

3. **No data in response**
   - Look for: `No data extracted from OpenAI response!`
   - The response structure might have changed
   - Check the "Unexpected response structure" warning

4. **API key issues**
   - Look for: `No OpenAI API key configured`
   - Verify `.env` file has correct `OPENAI_API_KEY`

#### Issue: "Apify scraping failed"

**Check the logs for:**
```
ERROR:app.services.scraper:Error fetching LinkedIn posts from Apify
```

**Common causes:**

1. **Invalid API key**
   - Verify `APIPY_API_KEY` in `.env`
   - Test with: `python test_scraper.py`

2. **Actor not found**
   - Ensure actor ID is correct: `apimaestro/linkedin-posts-search-scraper-no-cookies`
   - Check Apify dashboard for actor availability

3. **Content is a dict, not string**
   - ✅ Fixed: Added type checking in scraper
   - Look for: `'dict' object has no attribute 'strip'`

4. **Timeout**
   - Apify actors can take 30-60 seconds
   - Check for: `Actor run status: RUNNING`

#### Issue: "ModuleNotFoundError: No module named 'apify_client'"

**Solution:**
```bash
cd backend
source .venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

## Detailed Logging Output

### What to look for in logs:

#### Successful Scraper Run:
```
INFO:app.services.scraper:Starting Apify actor for queries: ['AI', 'LLM', 'GPT-5', 'Claude']
INFO:app.services.scraper:Fetched 15 posts from Apify
INFO:app.services.scraper:Successfully normalized 15 posts
```

#### Successful Analyzer Run:
```
INFO:app.services.analyzer:Starting OpenAI analysis for 15 posts
DEBUG:app.services.analyzer:Prepared 15 items for analysis
INFO:app.services.analyzer:Calling OpenAI API...
INFO:app.services.analyzer:OpenAI API call successful. Status: gpt-4o-mini, Usage: ...
INFO:app.services.analyzer:Found 'analyses' key with 15 items
INFO:app.services.analyzer:Successfully analyzed 15 posts via OpenAI
```

## Manual Testing

### Test OpenAI API directly:

```python
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=10
)
print(resp.choices[0].message.content)
```

### Test Apify API directly:

```python
from apify_client import ApifyClient
from app.config import settings

client = ApifyClient(settings.apify_api_key)
run = client.actor("apimaestro/linkedin-posts-search-scraper-no-cookies").call(
    run_input={"search_keyword": "AI", "page_number": 1}
)
items = client.dataset(run["defaultDatasetId"]).list_items().items
print(f"Fetched {len(items)} items")
```

## Environment Variables

Verify your `.env` file:

```bash
cat backend/.env
```

Should contain:
```
OPENAI_API_KEY=sk-proj-...
APIPY_API_KEY=apify_api_...
DATABASE_URL=sqlite:///./sentiment.db
FRONTEND_ORIGIN=http://localhost:5173
```

## Key Changes Made for Debugging

1. **Enhanced logging in `analyzer.py`:**
   - Log prompt lengths
   - Log raw OpenAI responses
   - Log JSON parsing steps
   - Log each post analysis result
   - Better error messages with exception types

2. **Enhanced logging in `scraper.py`:**
   - Log Apify API calls
   - Log data normalization steps
   - Handle dict/string content types
   - Better error messages

3. **Global logging config in `main.py`:**
   - Set to DEBUG level
   - Formatted timestamps and log levels

4. **Unit tests:**
   - `test_analyzer.py`: Tests OpenAI integration
   - `test_scraper.py`: Tests Apify integration

## Next Steps

1. Run the unit tests to identify specific failures
2. Check the detailed logs when running the backend
3. If issues persist, share the relevant log output for further debugging
