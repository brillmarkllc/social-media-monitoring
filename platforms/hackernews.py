import aiohttp
from datetime import datetime
from .base import Platform
from models import Mention
from config import Config
from typing import List


class HackerNews(Platform):
    def __init__(self, config: Config):
        self.config = config
        self.base_url = "http://hn.algolia.com/api/v1"
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        async with aiohttp.ClientSession() as session:
            # Search stories and comments
            async with session.get(
                f"{self.base_url}/search?query={keyword}&tags=(story,comment)"
            ) as response:
                data = await response.json()
                hits = data.get('hits', [])[:10]
                
                mentions = []
                for hit in hits:
                    mention = Mention(
                        platform="Hacker News",
                        title=hit.get('title', ''),
                        url=hit.get('url', f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                        description=hit.get('comment_text', hit.get('story_text', '')),
                        date=datetime.fromtimestamp(hit['created_at_i'])
                    )
                    mentions.append(mention)
                
                return mentions