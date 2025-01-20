import aiohttp
from datetime import datetime
from typing import List, Dict, Optional
from .base import Platform
from models import Mention
from config import Config


class Wikipedia(Platform):
    def __init__(self, config: Config):
        self.config = config
        self.base_url = f"https://{config.WIKIPEDIA_LANGUAGE}.wikipedia.org/w/api.php"
        self.headers = {}
        if config.WIKIPEDIA_ACCESS_TOKEN and config.WIKIPEDIA_CLIENT_SECRET:
            self.headers = {
                "Authorization": f"Bearer {config.WIKIPEDIA_ACCESS_TOKEN}",
                "Client-Secret": config.WIKIPEDIA_CLIENT_SECRET
            }

    async def _search_articles(self, session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search for Wikipedia articles using opensearch"""
        params = {
            "action": "opensearch",
            "namespace": "0",
            "search": keyword,
            "limit": "10",
            "format": "json"
        }
        
        async with session.get(self.base_url, params=params) as response:
            data = await response.json()
            # OpenSearch returns [query, titles, descriptions, urls]
            results = []
            for title, desc, url in zip(data[1], data[2], data[3]):
                results.append({
                    "title": title,
                    "description": desc,
                    "url": url
                })
            return results

    async def _get_article_details(self, session: aiohttp.ClientSession, title: str) -> Optional[Dict]:
        """Get detailed information about an article"""
        params = {
            "action": "query",
            "prop": "extracts|revisions|categories|pageviews",
            "titles": title,
            "exintro": True,  # Only get introduction
            "explaintext": True,  # Get plain text
            "rvprop": "timestamp",
            "format": "json",
            "redirects": True
        }
        
        async with session.get(self.base_url, params=params) as response:
            data = await response.json()
            pages = data["query"]["pages"]
            page = next(iter(pages.values()))
            
            if "missing" in page:
                return None
                
            return {
                "extract": page.get("extract", ""),
                "last_modified": page["revisions"][0]["timestamp"] if "revisions" in page else None,
                "categories": [cat["title"] for cat in page.get("categories", [])],
                "pageviews": sum(page.get("pageviews", {}).values()) if "pageviews" in page else 0
            }

    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        """Fetch mentions from Wikipedia"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            mentions = []
            
            # First get search results
            search_results = await self._search_articles(session, keyword)
            
            # Then get detailed information for each article
            for result in search_results:
                details = await self._get_article_details(session, result["title"])
                if not details:
                    continue
                
                # Create mention object with enhanced information
                mention = Mention(
                    platform="Wikipedia",
                    title=result["title"],
                    url=result["url"],
                    description=details["extract"][:500] if details["extract"] else result["description"],
                    date=datetime.strptime(details["last_modified"], "%Y-%m-%dT%H:%M:%SZ") if details["last_modified"] else None,
                    additional_fields={
                        "categories": ", ".join(details["categories"][:5]),  # First 5 categories
                        "pageviews_last_60_days": details["pageviews"],
                        "short_description": result["description"]
                    }
                )
                mentions.append(mention)
            
            return mentions