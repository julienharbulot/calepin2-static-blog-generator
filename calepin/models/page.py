from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from calepin.models.tag import TagSlug


class Format(Enum):
    text = "text"
    markdown = "markdown"


@dataclass
class Page:
    title: str
    content: str
    created: datetime
    url: str
    tags: List[TagSlug] = field(default_factory=list)
    summary: Optional[str] = None
    updated: Optional[datetime] = None
    published: Optional[datetime] = None
    draft: bool = False
    show_on_index: bool = True
    show_on_tags_pages: bool = True
    format: Format = Format.text
