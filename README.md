# LinkedIn Sentiment Tracker (Trend-In)

Lightweight full-stack MVP that analyzes sentiment of **real LinkedIn posts** across three categories.

- **Backend:** FastAPI, SQLAlchemy, OpenAI GPT-4o-mini for semantic sentiment analysis
- **Data Source:** Apify LinkedIn Posts Search Scraper (no cookies required)
- **Frontend:** React + Vite + Tailwind CSS with category tabs
- **Architecture:** Model-Controller-Service (MCS)

## Categories

1. **AI News** - Latest AI model comparisons (ChatGPT, Claude, Perplexity, Grok, etc.)
2. **Career Advice** - Interview tips and engineering advice from specific LinkedIn influencers
3. **New Research** - ArXiv papers and algorithm breakthroughs
