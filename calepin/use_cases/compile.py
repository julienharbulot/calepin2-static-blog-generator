from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Protocol

from calepin.models import Format, Page, Tag, TagSlug, Website


class Logger(Protocol):
    def warning(self, msg: str) -> None:
        pass


class Loader(Protocol):
    def get_pages(self) -> Iterator[Page]:
        pass


class Writer(Protocol):
    def write(self, website: Website):
        pass


class Formatter(Protocol):
    def formats(self) -> List[Format]:
        pass

    def process(self, content: str) -> str:
        pass


@dataclass
class CompileWebsiteUseCase:
    loader: Loader
    formatters: List[Formatter]
    writer: Writer
    logger: Logger

    _formatters_dict: Dict[Format, Formatter] = field(default_factory=dict)

    def __post_init__(self):
        for formatter in self.formatters:
            for fmt in formatter.formats():
                if fmt in self._formatters_dict:
                    raise Exception(
                        f"Multiple formatters attempting to register for format `{fmt}`"
                    )
                self._formatters_dict[fmt] = formatter

    def compile(self):
        pages = list(self.loader.get_pages())
        tags = self._extract_tags(pages)

        for p in pages:
            if p.format in self._formatters_dict:
                p.content = self._formatters_dict[p.format].process(p.content)

        self.writer.write(
            Website(
                pages=pages, tags=list(sorted(tags.values(), key=lambda tag: tag.slug))
            )
        )

    @staticmethod
    def _extract_tags(pages: Iterator[Page]) -> Dict[TagSlug, Tag]:
        tag: Dict[TagSlug, Tag] = dict()
        for p in pages:
            for tag_slug in p.tags:
                tag.setdefault(tag_slug, Tag(name=tag_slug, slug=tag_slug))
                tag[tag_slug].page_count += 1
        return tag
