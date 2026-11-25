import argparse
import json
import sys
from importlib import resources

from .client import SearchClient
from .providers.html_search import HtmlSearchProvider
from .providers.json_api import JsonApiProvider
from .safety import UnsafeQueryError


def load_providers(path=None):
    """Load configured providers or the packaged default site list."""
    if path is None:
        contents = resources.files("femboyfind").joinpath(
            "providers.default.json"
        ).read_text(encoding="utf-8")
        configs = json.loads(contents)
    else:
        with open(path, encoding="utf-8") as f:
            configs = json.load(f)

    providers = []
    for config in configs:
        config = dict(config)
        provider_type = config.pop("type", "json")
        if provider_type == "json":
            providers.append(JsonApiProvider(**config))
        elif provider_type == "html":
            providers.append(HtmlSearchProvider(**config))
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    return providers


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")

    ap = argparse.ArgumentParser(prog="femboyfind", description="Adults-only (18+) search client")
    ap.add_argument("extra", nargs="*", help="additional search terms")
    ap.add_argument(
        "--providers",
        help="path to providers.json (defaults to the built-in site list)",
    )
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--i-am-18", action="store_true", help="confirm that I am at least 18 years old")
    args = ap.parse_args(argv)

    if not args.i_am_18:
        sys.exit("18+ only. Add --i-am-18 to confirm that you are at least 18.")

    client = SearchClient(load_providers(args.providers))
    try:
        results = client.search(" ".join(args.extra), page=args.page,
                                limit=args.limit, exclude=args.exclude)
    except UnsafeQueryError as e:
        sys.exit(str(e))

    if args.json:
        print(json.dumps([r.__dict__ for r in results], ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"[{r.source}] {r.title}  {r.duration or ''}\n  {r.url}")
