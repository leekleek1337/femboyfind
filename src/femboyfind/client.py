from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, List, Optional

from .models import VideoResult
from .providers.base import Provider
from .safety import check_query

DEFAULT_TERM = "femboy"


class SearchClient:
    def __init__(self, providers: Iterable[Provider], base_term: str = DEFAULT_TERM):
        self.providers = list(providers)
        self.base_term = base_term

    def search(self, extra: str = "", page: int = 1, limit: int = 20,
               exclude: Optional[Iterable[str]] = None) -> List[VideoResult]:
        query = check_query(f"{self.base_term} {extra}".strip())
        banned = [w.lower() for w in (exclude or [])]

        def run(p: Provider) -> List[VideoResult]:
            try:
                return p.search(query, page=page, limit=limit)
            except Exception:       # один упавший провайдер не ломает остальных
                return []

        with ThreadPoolExecutor(max_workers=max(1, len(self.providers))) as ex:
            batches = list(ex.map(run, self.providers))

        seen, merged = set(), []
        for batch in batches:
            for r in batch:
                if r.url in seen:
                    continue
                title = str(r.title).lower()
                tags = (str(t).lower() for t in r.tags)
                tag_values = tuple(tags)
                if any(b in title or b in tag_values for b in banned):
                    continue
                seen.add(r.url)
                merged.append(r)
        return merged[:limit]
