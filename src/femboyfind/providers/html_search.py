import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import List

from ..models import VideoResult
from .base import Provider


class _AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self._active = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href") and self._active is None:
            self._active = {
                "href": attributes["href"],
                "title": attributes.get("title", ""),
                "text": [],
                "thumbnail": None,
            }
        elif tag == "img" and self._active is not None:
            self._active["thumbnail"] = (
                attributes.get("data-src")
                or attributes.get("data-original")
                or attributes.get("src")
            )
            if not self._active["title"]:
                self._active["title"] = attributes.get("alt", "")

    def handle_data(self, data):
        if self._active is not None:
            self._active["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._active is not None:
            self.links.append(self._active)
            self._active = None


class HtmlSearchProvider(Provider):
    """Search an adult site's public HTML results page without bypassing access controls."""

    def __init__(
        self,
        name: str,
        url_template: str,
        video_url_pattern: str,
        timeout: float = 15.0,
    ):
        self.name = name
        self.url_template = url_template
        self.video_url_pattern = re.compile(video_url_pattern, re.IGNORECASE)
        self.timeout = timeout
        self.headers = {"User-Agent": "femboyfind/0.1"}

    def search(self, query: str, page: int = 1, limit: int = 20) -> List[VideoResult]:
        if limit <= 0:
            return []
        url = self.url_template.format(
            query=urllib.parse.quote_plus(query),
            page=page,
            page_index=max(0, page - 1),
            limit=limit,
        )
        request = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            document = response.read().decode(charset, errors="replace")
            response_url = response.geturl()

        parser = _AnchorParser()
        parser.feed(document)

        results = []
        seen = set()
        for link in parser.links:
            path = urllib.parse.urlsplit(link["href"]).path
            if not self.video_url_pattern.search(path):
                continue
            title = link["title"] or " ".join(link["text"])
            title = " ".join(title.split())
            if not title:
                continue
            result_url = urllib.parse.urljoin(response_url, link["href"])
            if result_url in seen:
                continue
            seen.add(result_url)
            results.append(VideoResult(
                title=title,
                url=result_url,
                source=self.name,
                thumbnail=(
                    urllib.parse.urljoin(response_url, link["thumbnail"])
                    if link["thumbnail"]
                    else None
                ),
            ))
            if len(results) >= limit:
                break
        return results
