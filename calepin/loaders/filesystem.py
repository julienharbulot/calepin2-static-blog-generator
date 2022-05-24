import copy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterator, Optional, TextIO, Union, cast, overload

import pydantic
from dateutil import parser as dateutil_parser  # type: ignore
from pydantic import validator

from calepin.models.page import Format, Page
from calepin.utils.logger import Logger


@pydantic.dataclasses.dataclass(repr=False)
class FSPage(Page):
    @validator("created", "updated", "published", pre=True)
    def time_validate(cls, v):
        if v is None:
            return None
        return dateutil_parser.isoparse(v)

    @validator("tags", pre=True)
    def tags_validate(cls, v):
        tags = v.split() if isinstance(v, str) else v
        return [x.lower().strip() for x in tags]

    def __repr__(self):
        if self.content:
            cpy = copy.deepcopy(self)
            cpy.content = ""
            return repr(cpy)
        else:
            return super().__repr__()


@dataclass
class FileSystemLoader:
    root: Union[Path, str]
    logger: Logger

    def get_pages(self) -> Iterator[Page]:
        for filepath in Path(self.root).iterdir():
            if filepath.is_file():
                yield self.get_page(filepath)

    def get_page(self, filepath: Path) -> Page:
        try:
            return self._get_page(filepath)
        except Exception as e:
            raise Exception(f"Unable to read {str(filepath.name)}: {e}") from e

    def _get_page(self, filepath: Path) -> Page:
        with filepath.open("r") as f:
            frontmatter = self._parse_frontmatter(f)
            if filepath.suffix in [".md", ".mkd", ".markdown"]:
                frontmatter["format"] = Format.markdown

            text_content = f.read().strip()
            frontmatter["content"] = text_content
            frontmatter["url"] = filepath.stem + ".html"
            frontmatter.setdefault(
                "tags", ""
            )  # https://github.com/samuelcolvin/pydantic/issues/1537

            try:
                page = FSPage(**frontmatter)
            except TypeError as e:
                if "missing" in str(e) and "required positional argument" in str(e):
                    key = str(e).split(":")[-1].strip()
                    raise Exception(f"missing frontmatter key: {key}") from e

            return cast(Page, page)

    @staticmethod
    def _parse_frontmatter(f: TextIO):
        class State(Enum):
            frontmatter_delim = 1
            new_entry = 2
            quoted_str = 3

        state = State.frontmatter_delim
        frontmatter = dict()
        key = ""

        for line in f:
            line = line.strip()

            if state == State.frontmatter_delim:
                state = State.new_entry
                if set(line) == set("-"):
                    continue
                else:
                    pass  # fallback to next state with same line

            if state == State.new_entry:
                if set(line) == set("-"):
                    break  # we're done

                if ":" not in line:
                    raise Exception(
                        f"Expected frontmatter line to have format 'key: value' but found '{line}'"
                    )
                sep = line.find(":")
                key = line[:sep].strip()
                value = line[sep + 1 :].strip()
                if value.startswith('"'):
                    if not value.endswith('"'):
                        state = State.quoted_str
                    value = value.strip('"')
                frontmatter[key] = value
                continue

            if state == State.quoted_str:
                if line.endswith('"'):
                    state = State.new_entry
                    line = line.rstrip('"')
                frontmatter[key] += f"\n{line}"

        return frontmatter


@overload
def _parse_date(name: str, field: str, filepath: Path) -> datetime:
    ...


@overload
def _parse_date(name: str, field: Optional[str], filepath: Path) -> Optional[datetime]:
    ...


def _parse_date(
    name: str, field: Union[str, Optional[str]], filepath: Path
) -> Union[datetime, Optional[datetime]]:
    if field is None:
        return None
    try:
        print(f'"{field}"')
        return dateutil_parser.isoparse(field)
    except Exception as e:
        raise Exception(
            f"Unable to parse date field for frontmatter entry `{name}: {field}` in {str(filepath)}"
        ) from e


if __name__ == "__main__":
    fs = FileSystemLoader("./pages", Logger())
    from pprint import pprint

    pprint(list(fs.get_pages()))
