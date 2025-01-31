from googleapiclient.discovery import build
from datetime import datetime
from .base import Platform
from models import Mention
from config import Config
from typing import List
from time import sleep


class GoogleSearch(Platform):
    def __init__(self, config: Config, max_results: int = 10):
        self.config = config
        # Ensure max_results is a multiple of 10 (Google's page size)
        self.max_results = min(((max_results + 9) // 10) * 10, 100)
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        service = build("customsearch", "v1", developerKey=self.config.GOOGLE_API_KEY)
        mentions = []
        
        # Calculate number of pages needed
        pages = self.max_results // 10
        
        for page in range(pages):
            try:
                # Calculate start index (1-based)
                start_index = (page * 10) + 1
                
                res = service.cse().list(
                    q=keyword,
                    cx=self.config.SEARCH_ENGINE_ID,
                    num=10,
                    start=start_index
                ).execute()
                
                items = res.get('items', [])
                
                for item in items:
                    mention = Mention(
                        platform="Google Search",
                        title=item['title'],
                        url=item['link'],
                        description=item.get('snippet', ''),
                        date=None  # Google Search API doesn't provide dates
                    )
                    mentions.append(mention)
                
                # Add delay to respect rate limits
                if page < pages - 1:  # Don't sleep after the last page
                    sleep(1)
                    
            except Exception as e:
                print(f"Error fetching page {page + 1}: {str(e)}")
                break
        
        return mentions