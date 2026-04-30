import os
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "HuggingFaceH4/zephyr-7b-beta")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
USE_TWIKIT = os.getenv("USE_TWIKIT", "false").lower() == "true"
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
TWITTER_SCRAPER_ACTOR_ID = os.getenv("TWITTER_SCRAPER_ACTOR_ID", "apify/twitter-scraper")
APP_ENV = os.getenv("APP_ENV", "development")


class Settings:
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    MAILGUN_API_KEY: str = os.getenv("MAILGUN_API_KEY", "")
    MAILGUN_DOMAIN: str = os.getenv("MAILGUN_DOMAIN", "")
    MAILGUN_FROM: str = os.getenv("MAILGUN_FROM", "noreply@lmn8.com")


settings = Settings()
