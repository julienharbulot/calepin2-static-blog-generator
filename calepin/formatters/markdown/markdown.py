import re
from typing import List

import markdown  # type: ignore

from calepin.formatters.markdown import md_fenced_code
from calepin.models.page import Format

youtube_regex = re.compile(r"{% *youtube *(.+?) *%}")
youtube_data_regex = re.compile(r"([\S]+)(\s+([\d%]+)\s([\d%]+))?")


def handle_yt_match(match):
    width, height = 640, 390
    match = youtube_data_regex.search(match[1])
    if not match:
        return ""
    groups = match.groups()
    youtube_id = groups[0]
    width = groups[2] or width
    height = groups[3] or height
    youtube_out = """<span class="videobox"><iframe width="{width}" height="{height}" src='https://www.youtube.com/embed/{youtube_id}' frameborder='0' webkitAllowFullScreen mozallowfullscreen allowFullScreen> </iframe></span>""".format(
        width=width, height=height, youtube_id=youtube_id
    ).strip()
    return youtube_out


def parse_youtube_tags(articles, ctx):
    for article in articles.values():
        if article.dirty and "content" in article:
            article.content = youtube_regex.sub(handle_yt_match, article.content)


# ----------------------------------------------------------------------------------


class MarkdownFormatter:
    def __init__(self):
        MARKDOWN_EXTENSIONS = {
            "markdown.extensions.extra": {},
            "markdown.extensions.meta": {},
            "markdown.extensions.toc": {"title": "Table of contents"},
            "mdx_math": {},
        }
        ADDITIONAL_EXTENSIONS = [
            md_fenced_code.FencedCodeExtension(
                codehilite_config={"css_class": "hll", "guess_lang": False}
            ),
        ]

        self.md_parser = markdown.Markdown(
            extensions=ADDITIONAL_EXTENSIONS + list(MARKDOWN_EXTENSIONS.keys()),  # type: ignore
            extension_configs=MARKDOWN_EXTENSIONS,
        )

    def process(self, content) -> str:
        content = self.md_parser.convert(content)
        self.md_parser.reset()
        return content

    def formats(self) -> List[Format]:
        return [Format.markdown]
