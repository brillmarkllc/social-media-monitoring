from datetime import datetime
from typing import List
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from .base import Platform
from models import Mention
from config import Config

class Telegram(Platform):
    def __init__(self, config: Config):
        self.config = config
        # You'll need to get these from https://my.telegram.org/apps
        self.api_id = "your_api_id"  
        self.api_hash = "your_api_hash"
        self.channels = config.TELEGRAM_SEARCH_CHANNELS
        
    async def _init_client(self):
        """Initialize Telegram client"""
        client = TelegramClient('keyword_analyzer_bot', self.api_id, self.api_hash)
        await client.start(bot_token=self.config.TELEGRAM_BOT_TOKEN)
        return client
    
    async def _search_channel(self, client, channel: str, keyword: str) -> List[Mention]:
        """Search for messages in a specific channel"""
        mentions = []
        try:
            # Join the channel if not already joined
            channel_entity = await client.get_entity(channel)
            
            # Search for messages containing the keyword
            messages = await client(SearchRequest(
                peer=channel_entity,
                q=keyword,
                filter=InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_id=0,
                add_offset=0,
                limit=10,
                max_id=0,
                min_id=0,
                hash=0
            ))
            
            for msg in messages.messages:
                # Skip empty messages
                if not msg.message:
                    continue
                    
                # Create mention object
                mention = Mention(
                    platform="Telegram",
                    title=f"Message in @{channel}",
                    url=f"https://t.me/{channel}/{msg.id}",
                    description=msg.message[:500],  # Truncate long messages
                    date=msg.date,
                    additional_fields={
                        'channel': channel,
                        'views': getattr(msg, 'views', 0),
                        'forwards': getattr(msg, 'forwards', 0),
                        'replies': getattr(msg, 'replies', 0) if hasattr(msg, 'replies') else 0
                    }
                )
                mentions.append(mention)
                
        except Exception as e:
            print(f"Error searching channel {channel}: {str(e)}")
            
        return mentions
    
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        """Fetch mentions from multiple Telegram channels"""
        client = await self._init_client()
        try:
            all_mentions = []
            
            # Search each channel in parallel
            search_tasks = [
                self._search_channel(client, channel, keyword)
                for channel in self.channels
            ]
            
            # Gather results
            channel_results = await asyncio.gather(*search_tasks)
            for mentions in channel_results:
                all_mentions.extend(mentions)
            
            # Sort by date
            all_mentions.sort(key=lambda x: x.date, reverse=True)
            
            # Return top 10 most recent mentions
            return all_mentions[:10]
            
        finally:
            await client.disconnect()