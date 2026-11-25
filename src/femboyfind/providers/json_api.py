"""Универсальный провайдер для любого сайта с легальным JSON API.

Вы описываете URL-шаблон и где в ответе лежат поля — код сайта не зашит в библиотеку.
"""
import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ..models import VideoResult
from .base import Provider


def dig(data: Any, path: str) -> Any:
    """dig(d, 'a.b.0.c') -> d['a']['b'][0]['c']; None, если пути нет."""
    cur = data
    for part in path.split(".") if path else []:
        if isinstance(cur, list) and part.isdigit():
            idx = int(part)
            cur = cur[idx] if idx < len(cur) else None
        elif isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
        if cur is None:
            return None
    return cur


class JsonApiProvider(Provider):
    def __init__(
        self,
        name: str,
        url_template: str,            # напр. "https://api.example.com/search?q={query}&page={page}&per_page={limit}"
        results_path: str,            # где в JSON список результатов, напр. "data.videos"
        fields: Dict[str, str],       # {"title": "title", "url": "link", "thumbnail": "thumb.src", "duration": "length"}
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 15.0,
    ):
        self.name = name
        self.url_template = url_template
        self.results_path = results_path
        self.fields = fields
        self.headers = {"User-Agent": "femboyfind/0.1", **(headers or {})}
        self.timeout = timeout

    def search(self, query: str, page: int = 1, limit: int = 20) -> List[VideoResult]:
        url = self.url_template.format(
            query=urllib.parse.quote_plus(query), page=page, limit=limit
        )
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        items = dig(payload, self.results_path) or []
        out: List[VideoResult] = []
        for item in items:
            title = dig(item, self.fields.get("title", "title"))
            link = dig(item, self.fields.get("url", "url"))
            if not title or not link:
                continue
            tags = dig(item, self.fields.get("tags", "")) if "tags" in self.fields else None
            duration = dig(item, self.fields["duration"]) if "duration" in self.fields else None
            out.append(VideoResult(
                title=str(title),
                url=str(link),
                source=self.name,
                thumbnail=dig(item, self.fields["thumbnail"]) if "thumbnail" in self.fields else None,
                duration=str(duration) if duration is not None else None,
                tags=tuple(map(str, tags)) if isinstance(tags, list) else (),
            ))
        return out[:limit]
