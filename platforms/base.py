from abc import ABC, abstractmethod
from typing import List
from models import Mention

class Platform(ABC):
    @abstractmethod
    async def fetch_mentions(self, keyword: str) -> List[Mention]:
        pass