from dataclasses import dataclass
from dotenv import load_dotenv
from typing import List
import os


load_dotenv()


@dataclass
class Config:
    GOOGLE_API_KEY: str = os.environ.get('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID: str = os.environ.get('SEARCH_ENGINE_ID')
    YOUTUBE_API_KEY: str = os.environ.get('YOUTUBE_API_KEY')
    STACKEXCHANGE_KEY: str = os.environ.get('STACKEXCHANGE_KEY')
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY')
    GITHUB_TOKEN: str = os.environ.get('GITHUB_TOKEN')
    REDDIT_CLIENT_ID: str = "your_reddit_client_id"
    REDDIT_CLIENT_SECRET: str = "your_reddit_client_secret"
    REDDIT_USER_AGENT: str = "keyword_analyzer_bot/1.0"
    MASTODON_ACCESS_TOKEN: str = "your_mastodon_access_token"
    MASTODON_INSTANCE: str = "mastodon.social"  # or your preferred instance
    HN_API_KEY: str = "your_hn_api_key"
    OUTPUT_DIR: str = "output/csv"

    WIKIPEDIA_ACCESS_TOKEN: str = os.environ.get('WIKIPEDIA_ACCESS_TOKEN')  # Optional
    WIKIPEDIA_CLIENT_SECRET: str = os.environ.get('WIKIPEDIA_CLIENT_SECRET')  # Optional
    WIKIPEDIA_LANGUAGE: str = "en"  # Default language

    CURRENT_NEWS_API_KEY: str = os.environ.get('CURRENT_NEWS_API_KEY')
    CURRENT_NEWS_LANGUAGE: str = "en"  # Default language

    TELEGRAM_BOT_TOKEN: str = "your_telegram_bot_token"
    TELEGRAM_SEARCH_CHANNELS: List[str] = None  # List of channel/group usernames to search

    def __post_init__(self):
        # Default public channels/groups to search if none specified
        if self.TELEGRAM_SEARCH_CHANNELS is None:
            self.TELEGRAM_SEARCH_CHANNELS = [
                "cryptocurrency",
                "pythonprogramming",
                "machinelearning",
                "technology",
                "startup",
                # Add more default channels as needed
            ]