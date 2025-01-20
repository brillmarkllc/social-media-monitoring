from datetime import datetime
import aiohttp
from typing import List, Dict
from .base import Platform
from models import Mention
from config import Config


class CurrentNews(Platform):
    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://api.currentsapi.services/v1/search"
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        """Fetch news articles from CurrentNews API"""
        params = {
            'keywords': keyword,
            'language': self.config.CURRENT_NEWS_LANGUAGE,
            'apiKey': self.config.CURRENT_NEWS_API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                data = await response.json()
                
                if data['status'] != 'ok':
                    print(f"CurrentNews API error: {data.get('message', 'Unknown error')}")
                    return []
                
                mentions = []
                for article in data.get('news', []):
                    try:
                        # Parse the published date
                        published_date = datetime.strptime(
                            article['published'].split(' +')[0],  # Remove timezone part
                            "%Y-%m-%d %H:%M:%S"
                        )
                        
                        mention = Mention(
                            platform="CurrentNews",
                            title=article['title'],
                            url=article['url'],
                            description=article['description'],
                            date=published_date,
                            # additional_fields={
                            #     'author': article.get('author', 'Unknown'),
                            #     'categories': ', '.join(article.get('category', [])),
                            #     'language': article.get('language', 'en'),
                            #     'image_url': article.get('image', None)
                            # }
                        )
                        mentions.append(mention)
                        
                    except (KeyError, ValueError) as e:
                        print(f"Error processing article: {str(e)}")
                        continue
                
                return mentions