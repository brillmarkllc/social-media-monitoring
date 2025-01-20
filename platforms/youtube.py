from googleapiclient.discovery import build
from datetime import datetime
from .base import Platform
from models import Mention
from config import Config
from typing import List


class YouTube(Platform):
    def __init__(self, config: Config):
        self.config = config
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        youtube = build('youtube', 'v3', developerKey=self.config.YOUTUBE_API_KEY)
        
        request = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            maxResults=10
        )
        response = request.execute()
        
        mentions = []
        for item in response['items']:
            snippet = item['snippet']
            mention = Mention(
                platform="YouTube",
                title=snippet['title'],
                url=f"https://youtube.com/watch?v={item['id']['videoId']}",
                description=snippet['description'],
                date=datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
            )
            mentions.append(mention)
            
        return mentions