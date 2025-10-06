# Tests

Comprehensive unit tests for the LinkedIn Sentiment Analysis application.

## Test Files

### test_data_extraction.py
Tests the data extraction logic from Apify responses.

**What it tests:**
- Author dict vs string extraction
- Post metadata extraction (title, URL)
- Content dict extraction
- Missing fields handling
- Full normalization process

**Run:**
```bash
python tests/test_data_extraction.py
```

**Expected:** 6/6 tests pass

---

### test_scraper.py
Tests the LinkedIn scraper integration with Apify API.

**What it tests:**
- Apify API connection
- Real LinkedIn post fetching
- Field type validation (no dicts in strings)
- Mock data fallback

**Run:**
```bash
python tests/test_scraper.py
```

**Expected:** 3/3 tests pass
**Note:** Requires valid APIPY_API_KEY in .env

---

### test_analyzer.py
Tests the sentiment analysis with OpenAI API.

**What it tests:**
- OpenAI API connection
- Sentiment analysis accuracy
- Model configuration (gpt-5-nano)
- Heuristic fallback
- Full analyze_posts() function

**Run:**
```bash
python tests/test_analyzer.py
```

**Expected:** 3/3 tests pass
**Note:** Requires valid OPENAI_API_KEY in .env

---

## Running All Tests

```bash
cd backend

# Run all tests
python tests/test_data_extraction.py && \
python tests/test_scraper.py && \
python tests/test_analyzer.py

# Or individually
python tests/test_analyzer.py
```

## Test Coverage

- ✅ Data extraction from complex nested structures
- ✅ Author dict/string handling
- ✅ Post title/URL extraction
- ✅ Content dict parsing
- ✅ API integrations (Apify, OpenAI)
- ✅ Sentiment analysis logic
- ✅ Fallback mechanisms

## Requirements

Tests require:
- Valid `.env` file with API keys
- Python packages from `requirements.txt`
- SQLite (sentiment.db will be created if needed)

## Debugging Failed Tests

If tests fail:

1. **Check API keys:** Verify `.env` has valid keys
2. **Check logs:** Tests use DEBUG level logging
3. **Check network:** Some tests require internet access
4. **Check rate limits:** Apify/OpenAI may throttle requests

See `../DEBUGGING.md` for detailed troubleshooting.
