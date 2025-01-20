from datetime import datetime
import aiohttp
from .base import Platform
from models import Mention
from config import Config
from typing import List


class StackExchange(Platform):
    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://api.stackexchange.com/2.3"
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        async with aiohttp.ClientSession() as session:
            params = {
                'site': 'stackoverflow',
                'key': self.config.STACKEXCHANGE_KEY,
                'intitle': keyword,
                'pagesize': 10,
                'order': 'desc',
                'sort': 'activity'
            }
            
            async with session.get(f"{self.base_url}/search", params=params) as response:
                data = await response.json()
                
                mentions = []
                for item in data['items']:
                    mention = Mention(
                        platform="Stack Exchange",
                        title=item['title'],
                        url=item['link'],
                        description=item.get('excerpt', ''),
                        date=datetime.fromtimestamp(item['creation_date'])
                    )
                    mentions.append(mention)
                    
                return mentions