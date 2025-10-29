import os
from functools import lru_cache
from typing import Optional


class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL"
        # Production: e.g., "postgresql+psycopg://user:pass@host:5432/autoteamai"
        # Dev fallback:
        # "sqlite+aiosqlite:///./autoteamai.db",
    )


    # OpenAI / Provider config (agents.llm_client.OpenAIClient)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")


    # App
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENV: str = os.getenv("ENV", "development")


    # Prompt templates folder
    PROMPTS_DIR: str = os.getenv("PROMPTS_DIR", "config/prompts")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()