from datetime import datetime
import aiohttp
from .base import Platform
from models import Mention
from config import Config
from typing import List


class GitHub(Platform):
    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://api.github.com"
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        headers = {
            "Authorization": f"token {self.config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            # Search repositories and issues
            queries = [
                f"{self.base_url}/search/repositories?q={keyword}&sort=updated&order=desc",
                f"{self.base_url}/search/issues?q={keyword}&sort=updated&order=desc"
            ]
            
            mentions = []
            for query in queries:
                async with session.get(query) as response:
                    data = await response.json()
                    items = data.get('items', [])[:5]  # Get top 5 from each type
                    
                    for item in items:
                        mention = Mention(
                            platform="GitHub",
                            title=item.get('title', item.get('name', '')),
                            url=item.get('html_url', ''),
                            description=item.get('description', ''),
                            date=datetime.strptime(item['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                        )
                        mentions.append(mention)
            
            return mentions