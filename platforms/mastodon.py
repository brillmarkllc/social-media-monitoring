from mastodon import Mastodon
from datetime import datetime
from .base import Platform
from models import Mention
from config import Config
from typing import List


class MastodonPlatform(Platform):
    def __init__(self, config: Config):
        self.mastodon = Mastodon(
            access_token=config.MASTODON_ACCESS_TOKEN,
            api_base_url=f"https://{config.MASTODON_INSTANCE}"
        )
        
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        # Search public toots
        results = self.mastodon.search(keyword, resolve=True)
        statuses = results.get('statuses', [])
        
        mentions = []
        for status in statuses[:10]:  # Get top 10 results
            mention = Mention(
                platform="Mastodon",
                title=f"Toot by @{status['account']['username']}",
                url=status['url'],
                description=status['content'][:500],
                date=datetime.strptime(status['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            )
            mentions.append(mention)
            
        return mentions