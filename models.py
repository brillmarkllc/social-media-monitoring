from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Mention:
    platform: str
    title: str
    url: str
    description: str
    date: Optional[datetime]
    sentiment: Optional[str] = None

@dataclass
class PlatformReport:
    platform: str
    mentions: List[Mention]
    summary: Optional[str] = None