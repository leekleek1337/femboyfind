from email.message import Message
from pathlib import Path

import pytest
import femboyfind.cli as cli
import femboyfind.providers.html_search as html_search
from femboyfind import check_query, UnsafeQueryError
from femboyfind.cli import load_providers
from femboyfind.providers.html_search import HtmlSearchProvider
from femboyfind.providers.json_api import dig


def test_default_providers_include_sites_and_example_matches():
    providers = load_providers()
    names = {provider.name for provider in providers}
    assert names == {"eporner", "pornhub", "redtube", "xhamster", "xvideos", "xnxx"}
    assert any(isinstance(provider, HtmlSearchProvider) for provider in providers)

    example_path = Path(__file__).parents[1] / "providers.json"
    example_names = {provider.name for provider in load_providers(str(example_path))}
    assert example_names == names


def test_cli_uses_default_providers_when_option_is_omitted(monkeypatch):
    observed = {}

    class Client:
        def __init__(self, providers):
            observed["names"] = {provider.name for provider in providers}

        def search(self, *args, **kwargs):
            return []

    monkeypatch.setattr(cli, "SearchClient", Client)
    cli.main(["--i-am-18"])

    assert observed["names"] == {
        "eporner", "pornhub", "redtube", "xhamster", "xvideos", "xnxx"
    }


def test_html_search_provider_extracts_video_links(monkeypatch):
    class Response:
        headers = Message()

        def __init__(self):
            self.headers["Content-Type"] = "text/html; charset=utf-8"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return (
                b'<a href="/video.abc/title"><img src="/thumb.jpg" alt="A title"></a>'
                b'<a href="/category/ignore">Not a video</a>'
                b'<a href="/video.def/second" title="Second title"></a>'
            )

        def geturl(self):
            return "https://example.test/search?q=test"

    requested = []

    def fake_urlopen(request, timeout):
        requested.append(request.full_url)
        return Response()

    monkeypatch.setattr(html_search.urllib.request, "urlopen", fake_urlopen)
    provider = HtmlSearchProvider(
        name="example",
        url_template="https://example.test/search?q={query}&p={page_index}",
        video_url_pattern=r"^/video\.",
    )

    results = provider.search("femboy cosplay", page=1, limit=2)
    assert requested == ["https://example.test/search?q=femboy+cosplay&p=0"]
    assert [result.title for result in results] == ["A title", "Second title"]
    assert results[0].url == "https://example.test/video.abc/title"
    assert results[0].thumbnail == "https://example.test/thumb.jpg"


def test_dig():
    assert dig({"a": {"b": [{"c": 5}]}}, "a.b.0.c") == 5
    assert dig({"a": 1}, "x.y") is None


def test_safety():
    assert check_query("femboy cosplay") == "femboy cosplay"
    with pytest.raises(UnsafeQueryError):
        check_query("femboy teen")
    with pytest.raises(UnsafeQueryError):
        check_query("femboy школьник")
