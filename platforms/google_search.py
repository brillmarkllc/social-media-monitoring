from googleapiclient.discovery import build
from datetime import datetime
from .base import Platform
from models import Mention
from config import Config
from typing import List


class GoogleSearch(Platform):
    def __init__(self, config: Config):
        self.config = config
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        service = build("customsearch", "v1", developerKey=self.config.GOOGLE_API_KEY)
        res = service.cse().list(q=keyword, cx=self.config.SEARCH_ENGINE_ID, num=10).execute()
        items = res.get('items', [])
        
        mentions = []
        for item in items:
            mention = Mention(
                platform="Google Search",
                title=item['title'],
                url=item['link'],
                description=item.get('snippet', ''),
                date=None  # Google Search API doesn't provide dates
            )
            mentions.append(mention)
        
        return mentions