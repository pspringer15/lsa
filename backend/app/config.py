import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    apify_api_key: str | None = os.getenv("APIPY_API_KEY")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/sentiment_db")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

settings = Settings()
