from abc import ABC, abstractmethod
from typing import List
from ..models import VideoResult


class Provider(ABC):
    name: str = "provider"

    @abstractmethod
    def search(self, query: str, page: int = 1, limit: int = 20) -> List[VideoResult]:
        ...
