from dataclasses import dataclass
from typing import List

from .page import Page
from .tag import Tag


@dataclass
class Website:
    pages: List[Page]
    tags: List[Tag]
