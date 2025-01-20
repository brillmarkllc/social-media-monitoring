import asyncpraw
from datetime import datetime
from .base import Platform
from models import Mention
from config import Config
from typing import List


class Reddit(Platform):
    def __init__(self, config: Config):
        self.config = config
        self.reddit = asyncpraw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT
        )
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        mentions = []
        
        # Search submissions
        async for submission in self.reddit.subreddit("all").search(keyword, limit=10):
            mention = Mention(
                platform="Reddit",
                title=submission.title,
                url=f"https://reddit.com{submission.permalink}",
                description=submission.selftext[:500] if submission.selftext else "No description available",
                date=datetime.fromtimestamp(submission.created_utc)
            )
            mentions.append(mention)
            
        return mentions