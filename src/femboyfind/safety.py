"""Базовая защита: библиотека предназначена только для контента с совершеннолетними."""
import re
import unicodedata

_BLOCKED = re.compile(
    r"(?<!\w)(?:"
    r"children?|kids?|minors?|under[\s_-]*age|teens?|preteens?|"
    r"lolis?\w*|shotas?\w*|jailbait|young[\s_-]*boys?|little[\s_-]*boys?|"
    r"school[\s_-]*boys?|schoolboys?|"
    r"1[0-7][\s.-]*(?:yo|y\.o\.|years?(?:[\s_-]*old)?)"
    r"|ребен\w*|ребён\w*|дет[еийям]\w*|малолет\w*|несовершеннолет\w*|"
    r"школьниц[аы]?\w*|школьник\w*|лоли\w*|шота\w*"
    r")(?!\w)",
    re.IGNORECASE,
)


class UnsafeQueryError(ValueError):
    """Запрос выглядит так, будто касается несовершеннолетних."""


def check_query(query: str) -> str:
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    query = unicodedata.normalize("NFKC", query)
    if _BLOCKED.search(query):
        raise UnsafeQueryError("Query rejected: only adult (18+) content is supported.")
    return query.strip()
