from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class VideoResult:
    title: str
    url: str
    source: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    tags: tuple = field(default_factory=tuple)
